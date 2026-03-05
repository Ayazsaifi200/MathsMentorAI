"""
OCR Processor for Math Mentor AI
Handles image-to-text extraction using both Tesseract OCR and Groq Vision LLM
"""

import os
import logging
import base64
import io
import re
from typing import Dict, Any, Optional, Union
from pathlib import Path

import numpy as np
from PIL import Image
import requests

# Import configuration
from src.config import config
from src.input_processing.text_processor import TextProcessor

# Tesseract OCR (optional, fallback if not available)
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    import cv2
    TESSERACT_AVAILABLE = True
    logging.info("Tesseract OCR is available")
except ImportError:
    logging.warning("Tesseract OCR not available - will use Groq Vision only")


class OCRProcessor:
    """Processes images to extract mathematical text using OCR and Vision LLM"""
    
    def __init__(self):
        """Initialize OCR processor with Tesseract and Groq Vision"""
        self.logger = logging.getLogger(__name__)
        self.setup_tesseract()
        
        # Initialize text processor for LaTeX/Unicode conversion
        self.text_processor = TextProcessor()
        
        # Groq Vision configuration
        self.groq_api_key = config.GROQ_API_KEY
        self.groq_vision_model = config.GROQ_VISION_MODEL
        self.use_groq_vision = config.USE_GROQ_VISION
        
        self.logger.info(f"OCR Processor initialized - Tesseract: {TESSERACT_AVAILABLE}, Groq Vision: {self.use_groq_vision}")
    
    def setup_tesseract(self):
        """Configure Tesseract OCR if available"""
        if not TESSERACT_AVAILABLE:
            return
        
        # Set Tesseract path from config
        if config.TESSERACT_PATH and os.path.exists(config.TESSERACT_PATH):
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
            self.logger.info(f"Tesseract path set to: {config.TESSERACT_PATH}")
            
            # Set TESSDATA_PREFIX environment variable
            if hasattr(config, 'TESSDATA_PREFIX') and config.TESSDATA_PREFIX:
                os.environ['TESSDATA_PREFIX'] = config.TESSDATA_PREFIX
                self.logger.info(f"TESSDATA_PREFIX set to: {config.TESSDATA_PREFIX}")
        else:
            self.logger.warning(f"Tesseract path not found: {config.TESSERACT_PATH}")
    
    def auto_crop_content(self, image: np.ndarray) -> np.ndarray:
        """
        Auto-detect and crop to main content area (removes browser UI, borders, whitespace)
        Uses adaptive detection for both light and dark backgrounds.
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            h, w = gray.shape
            
            # Detect background: use edge of image as reference
            mean_val = np.mean(gray)
            
            if mean_val < 140:
                # Dark background: find light content
                _, binary = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY)
            else:
                # Light background: find dark content
                _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Filter out tiny noise contours (< 1% of image area)
                min_area = h * w * 0.001
                valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
                
                if valid_contours:
                    # Get bounding box of all valid content
                    x_min = min(cv2.boundingRect(c)[0] for c in valid_contours)
                    y_min = min(cv2.boundingRect(c)[1] for c in valid_contours)
                    x_max = max(cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] for c in valid_contours)
                    y_max = max(cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] for c in valid_contours)
                    
                    # Add generous padding (important for math: don't cut off exponents at edges)
                    padding = max(30, int(min(h, w) * 0.03))
                    x_min = max(0, x_min - padding)
                    y_min = max(0, y_min - padding)
                    x_max = min(w, x_max + padding)
                    y_max = min(h, y_max + padding)
                    
                    cropped = image[y_min:y_max, x_min:x_max]
                    
                    # Only use crop if it removes significant border/UI
                    if cropped.shape[0] < h * 0.95 or cropped.shape[1] < w * 0.95:
                        self.logger.info(f"Auto-cropped: {h}x{w} -> {cropped.shape[0]}x{cropped.shape[1]}")
                        return cropped
            
            return image
        except Exception as e:
            self.logger.warning(f"Auto-crop failed: {e}")
            return image
    
    def _to_grayscale_upscaled(self, image: np.ndarray) -> np.ndarray:
        """Convert to grayscale and upscale for optimal Tesseract OCR.
        Uses LANCZOS4 at 2.5x for high-quality math symbol preservation.
        For dark backgrounds, inverts to light bg (black text on white) first.
        """
        image = self.auto_crop_content(image)
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # CRITICAL: Detect dark background and INVERT
        # Tesseract works best with dark text on light background
        mean_val = np.mean(gray)
        if mean_val < 140:
            gray = cv2.bitwise_not(gray)
            self.logger.info(f"Dark background detected (mean={mean_val:.0f}), inverted to light bg")
        
        h, w = gray.shape
        
        # 2.5x upscale with LANCZOS4 for sharp math symbols
        scale = max(2.5, 2500 / max(w, 1))
        new_w, new_h = int(w * scale), int(h * scale)
        if new_w > 5000:
            scale = 5000 / w
            new_w, new_h = int(w * scale), int(h * scale)
        
        if scale > 1.0:
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            self.logger.info(f"Upscale: {w}x{h} -> {new_w}x{new_h} ({scale:.1f}x)")
        
        return gray

    def preprocess_image_variants(self, image: np.ndarray) -> list:
        """
        Generate 5 diverse image variants for accurate math OCR.
        Each variant emphasizes different aspects of math notation.
        Returns list of (image, description) tuples.
        """
        if not TESSERACT_AVAILABLE:
            return [(image, 'original')]
        
        variants = []
        try:
            gray = self._to_grayscale_upscaled(image)
            h, w = gray.shape

            # Variant 1: Otsu threshold — clean binary for printed math
            _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append((otsu, 'otsu'))

            # Variant 2: Adaptive threshold — handles mixed font sizes (text + tiny super/subscripts)
            block_size = min(51, max(31, w // 80) | 1)
            adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, block_size, 10)
            variants.append((adaptive, 'adaptive'))

            # Variant 3: Sharpened + Otsu — enhances thin lines (√ bars, fraction lines)
            kernel_sharp = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
            sharpened = cv2.filter2D(gray, -1, kernel_sharp)
            _, sharp_otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append((sharp_otsu, 'sharp'))

            # Variant 4: Morphological close — connects broken strokes in √, ∫, ∑ symbols
            kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            morph = cv2.morphologyEx(otsu, cv2.MORPH_CLOSE, kernel_close)
            variants.append((morph, 'morph'))

            # Variant 5: CLAHE-enhanced for low-contrast text
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            _, enh_otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            variants.append((enh_otsu, 'clahe'))

        except Exception as e:
            self.logger.warning(f"Preprocessing failed: {e}")
            variants.append((image, 'original'))
        
        return variants

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Legacy method — returns best single preprocessed variant"""
        variants = self.preprocess_image_variants(image)
        return variants[0][0] if variants else image
    
    def fix_math_ocr_errors(self, text: str) -> str:
        """
        Minimal safe cleanup of OCR output for math text.
        Only fixes patterns that are unambiguously wrong.
        """
        # Remove noise patterns from screenshots
        text = re.sub(r'\bv\s+Startup\b.*?(?=JEE|Q\d|Let|Consider|Find|Solve|If|Given|$)', '', text)
        text = re.sub(r'\bmathongo\b', '', text, flags=re.IGNORECASE)
        
        # Fix x between digits -> multiplication
        text = re.sub(r'(?<=[0-9])\s*x\s*(?=[0-9])', ' × ', text)
        
        # Clean up multiple spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)
        
        # Remove control characters but keep newlines
        text = re.sub(r'[\x00-\x09\x0b-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def convert_to_math_unicode(self, text: str) -> str:
        """
        Minimal Unicode conversion: only convert explicit LaTeX-like commands
        (backslash-prefixed), never convert regular English words.
        """
        # Only convert explicit LaTeX backslash commands (like \sqrt, \frac)
        latex_cmds = {
            r'\\sqrt': '√', r'\\infty': '∞', r'\\infinity': '∞',
            r'\\sum': '∑', r'\\prod': '∏', r'\\int(?!e)': '∫',
            r'\\partial': '∂', r'\\nabla': '∇',
            r'\\leq': '≤', r'\\geq': '≥', r'\\neq': '≠',
            r'\\approx': '≈', r'\\equiv': '≡',
            r'\\alpha': 'α', r'\\beta': 'β', r'\\gamma': 'γ',
            r'\\delta': 'δ', r'\\theta': 'θ', r'\\pi': 'π',
            r'\\sigma': 'σ', r'\\phi': 'φ', r'\\omega': 'ω',
            r'\\pm': '±', r'\\times': '×', r'\\cdot': '·',
            r'\\div': '÷',
        }
        for pattern, symbol in latex_cmds.items():
            text = re.sub(pattern, symbol, text)
        
        # Convert ^2 and ^3 to superscripts only when directly after )
        text = re.sub(r'\)\^2\b', ')²', text)
        text = re.sub(r'\)\^3\b', ')³', text)
        
        # Clean up whitespace
        text = re.sub(r'\s{2,}', ' ', text)
        
        return text.strip()

    def _detect_missing_symbols(self, readings: list) -> str:
        """Analyze OCR readings to detect likely missing math symbols."""
        combined = ' '.join(text for text, _ in readings).lower()
        hints = []
        
        # Check for √ evidence — but NOT if there's integration (dt, dx)
        has_sqrt = '√' in combined or 'sqrt' in combined
        has_paren_expr = bool(re.search(r'\(1\s*[+\-±]\s*[\(\d]', combined))
        has_integral_evidence = bool(re.search(r'dt|dx|d\s*θ|d\s*x|f\(t\)|f\(x\)', combined))
        has_sequence = bool(re.search(r'a[_\s,.]?\s*[n₀₁₂]|t[_\s,.]?\s*[n₀₁₂]|s[_\s,.]?\s*[n₀₁₂]', combined))
        if not has_sqrt and has_paren_expr and not has_integral_evidence and has_sequence:
            hints.append("Hint: No √ found but sequence notation detected — Tesseract may have dropped √ symbols.")
        
        if hints:
            return "\n=== ANALYSIS HINTS ===\n" + "\n".join(hints) + "\n\n"
        return ""

    def reconstruct_math_with_llm(self, ocr_readings: list) -> str:
        """
        Use Groq Llama (text-only, NOT Vision) to reconstruct proper math
        from multiple noisy Tesseract OCR readings of the same image.
        """
        if not self.groq_api_key:
            self.logger.debug("No Groq API key — skipping LLM math reconstruction")
            return ocr_readings[0][0] if ocr_readings else ''
        
        if not ocr_readings:
            return ''
        
        # Strip image dimension metadata (e.g. "686 × 386") from each reading
        cleaned_readings = []
        for text, desc in ocr_readings:
            text = re.sub(r'\d{2,4}\s*[×xX*]\s*\d{2,4}\s*$', '', text, flags=re.MULTILINE).strip()
            if text:
                cleaned_readings.append((text, desc))
        
        if not cleaned_readings:
            return ocr_readings[0][0]
        
        # Build numbered readings block
        readings_block = ""
        for i, (text, desc) in enumerate(cleaned_readings, 1):
            readings_block += f"[Reading {i}]\n{text}\n\n"
        
        # Auto-detect likely missing symbols
        structure_hints = self._detect_missing_symbols(cleaned_readings)
        
        prompt = f"""You have {len(cleaned_readings)} noisy Tesseract OCR readings from the SAME math image.
Your job: reconstruct the text EXACTLY as it appears in the image, fixing only OCR noise.
{structure_hints}=== ABSOLUTE RULES ===
1. FAITHFULNESS IS #1 PRIORITY: Every word, symbol, and equation in your output MUST have evidence in at least one reading. Do NOT invent, add, or fabricate ANY content that is not supported by the readings.
2. If text is truncated/cut off in ALL readings, output it as truncated — do NOT complete or extend it.
3. NEVER add extra equations, lines, or problem parts that don't appear in any reading.
4. If a symbol appears in the SAME position across multiple readings as different characters, pick the most likely one.
5. Remove ONLY watermarks and OCR artifacts (random characters not part of any word).

=== OCR CORRECTION GUIDE ===
Tesseract garbles math symbols. Fix ONLY what you can verify from readings:

- "f", "J", "|" before "(t)dt" or with limits → ∫ (integral)
- "V", "v" before parenthesized expression (NO dt/dx nearby, sequence context) → possibly √
- Isolated small numbers after ) or variables → likely exponents (², ³)
- "a," "a." "a n" in sequence context → aₙ (subscript)
- "€" → ∈, "R" in set context → ℝ
- "4/" where n expected → likely n (Tesseract n→4 confusion)

=== OUTPUT FORMAT ===
Unicode: √ ∫ ∑ ∏ ∞ ± ≤ ≥ ≠ ≈ π θ α β γ δ σ φ ω ∈ ℝ
Superscripts: ⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ  Subscripts: ₀₁₂₃₄₅₆₇₈₉ₙᵢ
Fractions: (a/b) inline
Preserve ALL text: problem statement, conditions, questions, options.
Output ONLY the reconstructed text. No explanations. No extra content.

{readings_block}Corrected:"""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are a FAITHFUL math OCR reconstruction engine. You receive multiple noisy Tesseract OCR readings of ONE math image. Your ONLY job: clean up OCR noise and output the text as it appears in the image. CRITICAL RULES: 1) NEVER invent or fabricate content — every word/symbol must have evidence in the readings. 2) If text is cut off, leave it cut off — do NOT complete it. 3) Fix garbled math symbols: f/J/| before (t)dt → ∫, V/v before () in sequence context → possibly √, small numbers after ) → exponents. 4) Fix OCR character errors: € → ∈, R in set context → ℝ. 5) Preserve ALL text: statements, conditions, questions. 6) Unicode output: √∫∑ ⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ ₀₁₂₃ₙ ∞±≤≥≠≈πθαβγδ. Output ONLY the reconstructed text. NEVER explain. NEVER add content not in the readings.'
                    },
                    {
                        'role': 'user', 
                        'content': prompt
                    }
                ],
                'temperature': 0.0,
                'max_tokens': 1000
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                reconstructed = result['choices'][0]['message']['content'].strip()
                # Remove markdown code fences
                reconstructed = re.sub(r'^```\w*\n?', '', reconstructed)
                reconstructed = re.sub(r'\n?```$', '', reconstructed)
                # Remove any "MERGED OUTPUT:" prefix the LLM might echo
                reconstructed = re.sub(r'^MERGED\s*OUTPUT\s*:\s*', '', reconstructed, flags=re.IGNORECASE)
                reconstructed = reconstructed.strip()
                
                if len(reconstructed) >= 5:
                    self.logger.info(f"LLM math reconstruction ({len(reconstructed)} chars): {reconstructed}")
                    return reconstructed
                else:
                    self.logger.warning("LLM returned too-short result, keeping original")
                    return cleaned_readings[0][0]
            else:
                self.logger.warning(f"LLM reconstruction failed: HTTP {response.status_code}")
                return cleaned_readings[0][0]
                
        except Exception as e:
            self.logger.warning(f"LLM math reconstruction error: {e}")
            return cleaned_readings[0][0]

    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string for Groq Vision API
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded image string
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to JPEG bytes
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=95)
        img_bytes = buffered.getvalue()
        
        # Encode to base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return img_base64
    
    def extract_with_groq_vision(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text from image using Groq Vision LLM
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with extracted text, confidence, and metadata
        """
        if not self.groq_api_key:
            return {
                'extracted_text': '',
                'confidence': 0,
                'method': 'groq_vision',
                'error': 'Groq API key not configured'
            }
        
        try:
            # Convert image to base64
            img_base64 = self.image_to_base64(image)
            
            # Prepare API request - Groq format
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Groq Vision uses a simpler format
            payload = {
                'model': self.groq_vision_model,
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': (
                                    'Extract ALL mathematical text, equations, and problems from this image accurately. '
                                    'This is a JEE/competitive math problem. '
                                    'Use LaTeX notation for equations: \\sqrt{} for square roots, \\frac{}{} for fractions, '
                                    '^{} for exponents, _{} for subscripts, \\left( \\right) for parentheses. '
                                    'Example: If a_n = \\sqrt{1 + \\left(1 - \\frac{1}{n}\\right)^2} '
                                    'Preserve the EXACT mathematical structure. Do NOT solve, explain, or simplify. '
                                    'Return ONLY the extracted mathematical text/equations.'
                                )
                            },
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/jpeg;base64,{img_base64}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': config.GROQ_VISION_MAX_TOKENS,
                'temperature': 0.1
            }
            
            # Call Groq Vision API
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                # Estimate confidence
                confidence = self._estimate_vision_confidence(
                    extracted_text,
                    result['choices'][0].get('finish_reason', '')
                )
                
                self.logger.info(f"Groq Vision extraction successful - confidence: {confidence}%")
                
                return {
                    'extracted_text': extracted_text,
                    'confidence': confidence,
                    'method': 'groq_vision',
                    'model': self.groq_vision_model,
                    'processing_successful': True
                }
            else:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return {
                    'extracted_text': '',
                    'confidence': 0,
                    'method': 'groq_vision',
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Groq Vision extraction failed: {e}")
            return {
                'extracted_text': '',
                'confidence': 0,
                'method': 'groq_vision',
                'error': str(e)
            }
    
    def _estimate_vision_confidence(self, text: str, finish_reason: str) -> int:
        """
        Estimate confidence score for Groq Vision extraction
        
        Args:
            text: Extracted text
            finish_reason: API finish reason
            
        Returns:
            Confidence score (0-100)
        """
        # Base confidence for LLM extraction
        confidence = 70
        
        # Boost if contains mathematical symbols
        math_symbols = ['=', '+', '-', '/', '*', '^', '√', '∫', '∑', '∏', 'lim', 'sin', 'cos', 'tan']
        if any(symbol in text for symbol in math_symbols):
            confidence += 15
        
        # Boost if text is substantial
        if len(text) > 20:
            confidence += 10
        
        # Boost if API completed normally
        if finish_reason == 'stop':
            confidence += 5
        
        return min(confidence, 100)
    
    def _math_quality_score(self, text: str) -> int:
        """Score how math-like a text is (higher = more math content)"""
        score = 0
        # Reward math characters
        math_chars = set('=+-*/^()[]{}0123456789.,<>|')
        math_count = sum(1 for c in text if c in math_chars)
        score += math_count * 3
        # Reward math keywords
        for kw in ['If', 'if', 'sqrt', 'log', 'sin', 'cos', 'tan', 'lim', 'sum',
                    'IIT', 'JEE', 'find', 'Find', 'solve', 'Solve', 'prove', 'Prove']:
            if kw in text:
                score += 10
        # Reward equation-like patterns: letter = expression
        if re.search(r'[a-zA-Z]\s*=', text):
            score += 20
        # Reward fractions: number/number or (expr)/(expr)
        if re.search(r'\d\s*/\s*\d|\)/\(', text):
            score += 15
        # Penalize garbage (long runs of special chars with no alphanumerics)
        garbage_runs = re.findall(r'[^a-zA-Z0-9\s]{4,}', text)
        score -= len(garbage_runs) * 10
        return score

    def extract_text_with_confidence(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Smart OCR extraction: uses ALL variants for maximum accuracy,
        collects diverse readings, then LLM reconstructs the best math text.
        """
        if not TESSERACT_AVAILABLE:
            return {
                'extracted_text': '',
                'overall_confidence': 0,
                'method': 'tesseract',
                'error': 'Tesseract not available'
            }
        
        try:
            variants = self.preprocess_image_variants(image)
            
            all_readings = []
            best_text = ''
            best_score = -999
            best_confidence = 70
            best_desc = ''
            
            # 5 configs for maximum diversity — each PSM mode reads differently:
            # PSM 6 (block) + eng+equ: standard math equations
            # PSM 6 + eng: cleaner without equ noise 
            # PSM 4 (column) + eng+equ: multi-line problems, preserves structure
            # PSM 3 (auto) + eng+equ: complex layouts
            # PSM 11 (sparse) + eng: finds scattered text/symbols others miss
            configs = [
                ('--psm 6 --oem 3 --dpi 300', 'eng+equ', 'blk_eq'),
                ('--psm 6 --oem 3 --dpi 300', 'eng', 'blk_en'),
                ('--psm 4 --oem 3 --dpi 300', 'eng+equ', 'col_eq'),
                ('--psm 3 --oem 3 --dpi 300', 'eng+equ', 'auto'),
                ('--psm 11 --oem 3 --dpi 300', 'eng', 'sparse'),
            ]
            
            for img_variant, variant_name in variants:
                for psm_config, lang, config_desc in configs:
                    try:
                        text = pytesseract.image_to_string(
                            img_variant, lang=lang, config=psm_config
                        ).strip()
                        if not text or len(text) < 3:
                            continue
                        math_score = self._math_quality_score(text)
                        score = math_score + min(len(text), 300)
                        cleaned = self.fix_math_ocr_errors(text)
                        if cleaned and len(cleaned) >= 3:
                            desc = f"{variant_name}/{config_desc}"
                            all_readings.append((cleaned, desc, score))
                            if score > best_score:
                                best_score = score
                                best_text = cleaned
                                best_desc = desc
                    except Exception:
                        continue
            
            if not best_text:
                raise Exception("All OCR configurations failed")
            
            # Deduplicate: keep diverse readings sorted by quality score
            seen_texts = set()
            unique_readings = []
            all_readings.sort(key=lambda x: x[2], reverse=True)
            for text, desc, score in all_readings:
                normalized = re.sub(r'\s+', ' ', text.strip().lower())
                if normalized not in seen_texts:
                    seen_texts.add(normalized)
                    unique_readings.append((text, desc))
                    if len(unique_readings) >= 8:
                        break
            
            self.logger.info(
                f"Collected {len(unique_readings)} unique readings from {len(all_readings)} total"
            )
            
            # Log raw readings for debugging (full text)
            for i, (text, desc) in enumerate(unique_readings):
                self.logger.info(f"OCR Reading {i+1} [{desc}]: {text}")
            
            # LLM reconstruction from diverse readings
            extracted_text = self.reconstruct_math_with_llm(unique_readings)
            
            self.logger.info(
                f"OCR result ({best_desc}): {len(extracted_text)} chars, "
                f"conf={best_confidence}%, score={best_score}"
            )
            
            return {
                'extracted_text': extracted_text,
                'overall_confidence': best_confidence,
                'method': 'tesseract',
                'processing_successful': True,
                'word_count': len(extracted_text.split()),
                'raw_text': best_text
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'extracted_text': '',
                'overall_confidence': 0,
                'method': 'tesseract',
                'error': str(e)
            }
    
    def extract_with_hybrid(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text using both Tesseract and Groq Vision, select best result
        
        Args:
            image: PIL Image object
            
        Returns:
            Best extraction result with comparison metadata
        """
        results = {
            'tesseract': None,
            'groq_vision': None
        }
        
        # Try Tesseract OCR
        if TESSERACT_AVAILABLE:
            np_image = np.array(image)
            results['tesseract'] = self.extract_text_with_confidence(np_image)
            self.logger.info(f"Tesseract result: {results['tesseract'].get('overall_confidence', 0)}% confidence")
        
        # Try Groq Vision
        if self.use_groq_vision and self.groq_api_key:
            results['groq_vision'] = self.extract_with_groq_vision(image)
            self.logger.info(f"Groq Vision result: {results['groq_vision'].get('confidence', 0)}% confidence")
        
        # Select best result
        best_result = self._select_best_result(results)
        
        # Add comparison metadata
        final_result = self._format_final_result(best_result, results)
        
        return final_result
    
    def _select_best_result(self, results: Dict[str, Optional[Dict]]) -> Dict[str, Any]:
        """
        Select the best OCR result from available methods
        
        Args:
            results: Dictionary with tesseract and groq_vision results
            
        Returns:
            Best result
        """
        tesseract_result = results.get('tesseract')
        groq_result = results.get('groq_vision')
        
        # If only one method available, use it
        if tesseract_result and not groq_result:
            self.logger.info("Using Tesseract (only method available)")
            return tesseract_result
        
        if groq_result and not tesseract_result:
            self.logger.info("Using Groq Vision (only method available)")
            return groq_result
        
        # If both available, select based on confidence and quality
        if tesseract_result and groq_result:
            tesseract_conf = tesseract_result.get('overall_confidence', 0)
            groq_conf = groq_result.get('confidence', 0)
            
            # Prefer Groq if Tesseract confidence is low
            if tesseract_conf < 60 and groq_conf > 70:
                self.logger.info(f"Using Groq Vision (Tesseract low confidence: {tesseract_conf}%)")
                return groq_result
            
            # Prefer Tesseract if very high confidence (more precise)
            if tesseract_conf >= 80:
                self.logger.info(f"Using Tesseract (high confidence: {tesseract_conf}%)")
                return tesseract_result
            
            # For medium confidence, prefer Groq (better math understanding)
            if groq_conf >= tesseract_conf:
                self.logger.info(f"Using Groq Vision (better math understanding: {groq_conf}% vs {tesseract_conf}%)")
                return groq_result
            else:
                self.logger.info(f"Using Tesseract ({tesseract_conf}% vs Groq {groq_conf}%)")
                return tesseract_result
        
        # Fallback: return empty result
        return {
            'extracted_text': '',
            'confidence': 0,
            'method': 'none',
            'error': 'No OCR methods available'
        }
    
    def _format_final_result(self, best_result: Dict[str, Any], all_results: Dict[str, Optional[Dict]]) -> Dict[str, Any]:
        """
        Format final result with comparison metadata
        
        Args:
            best_result: Selected best result
            all_results: All extraction results
            
        Returns:
            Formatted result with comparison data
        """
        # Normalize confidence field name
        confidence = best_result.get('confidence') or best_result.get('overall_confidence', 0)
        
        # Add comparison metadata
        comparison = {
            'methods_tried': [],
            'tesseract_confidence': 0,
            'groq_confidence': 0
        }
        
        if all_results.get('tesseract'):
            comparison['methods_tried'].append('tesseract')
            comparison['tesseract_confidence'] = all_results['tesseract'].get('overall_confidence', 0)
        
        if all_results.get('groq_vision'):
            comparison['methods_tried'].append('groq_vision')
            comparison['groq_confidence'] = all_results['groq_vision'].get('confidence', 0)
        
        return {
            'extracted_text': best_result.get('extracted_text', ''),
            'confidence': confidence,
            'method': best_result.get('method', 'unknown'),
            'processing_successful': best_result.get('processing_successful', False),
            'comparison': comparison
        }
    
    def process_image_input(
        self,
        image_data: Union[str, np.ndarray, Image.Image],
        use_hybrid: bool = True
    ) -> Dict[str, Any]:
        """
        Process image input and extract text using available OCR methods
        
        Args:
            image_data: Image as file path, numpy array, or PIL Image
            use_hybrid: Whether to use hybrid extraction (both methods)
            
        Returns:
            Dictionary with extraction results
        """
        try:
            # Convert input to PIL Image for consistent processing
            if isinstance(image_data, str):
                # File path
                pil_image = Image.open(image_data)
            elif isinstance(image_data, np.ndarray):
                # NumPy array
                pil_image = Image.fromarray(image_data)
            elif isinstance(image_data, Image.Image):
                # Already PIL Image
                pil_image = image_data
            else:
                raise ValueError(f"Unsupported image type: {type(image_data)}")
            
            # Force Tesseract-only mode when Groq Vision is disabled
            if TESSERACT_AVAILABLE and not self.use_groq_vision:
                np_image = np.array(pil_image)
                result = self.extract_text_with_confidence(np_image)
                self.logger.info(f"Using Tesseract-only mode (Groq Vision disabled)")
            
            # Use hybrid extraction if both methods enabled
            elif use_hybrid and TESSERACT_AVAILABLE and self.use_groq_vision and self.groq_api_key:
                result = self.extract_with_hybrid(pil_image)
            
            # Fallback to single method
            elif self.use_groq_vision and self.groq_api_key:
                result = self.extract_with_groq_vision(pil_image)
            
            elif TESSERACT_AVAILABLE:
                np_image = np.array(pil_image)
                result = self.extract_text_with_confidence(np_image)
            
            else:
                result = {
                    'extracted_text': '',
                    'confidence': 0,
                    'method': 'none',
                    'error': 'No OCR methods available'
                }
            
            # Normalize confidence field (Tesseract uses 'overall_confidence', hybrid uses 'confidence')
            confidence = result.get('confidence') or result.get('overall_confidence', 0)
            has_error = 'error' in result
            has_text = bool(result.get('extracted_text', '').strip())
            
            self.logger.info(f"OCR processing completed. Confidence: {confidence:.2f}")
            
            return {
                'success': not has_error and has_text and confidence > 0,
                'text': result.get('extracted_text', ''),
                'error': result.get('error', '') if has_error else None,
                'raw_result': {
                    **result,
                    'confidence': confidence  # Ensure normalized 'confidence' field exists
                }
            }
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {e}")
            return {
                'success': False,
                'text': '',
                'error': str(e),
                'raw_result': {
                    'extracted_text': '',
                    'confidence': 0,
                    'error': str(e)
                }
            }
