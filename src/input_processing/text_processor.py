# -*- coding: utf-8 -*-
"""
Text Processing Module for Math Mentor AI
Handles direct text input processing and normalization
"""

import re
import logging
from typing import Dict, Any, List
import unicodedata

logger = logging.getLogger(__name__)

class TextProcessor:
    """Text processor for handling direct text input and normalization"""
    
    def __init__(self):
        """Initialize text processor"""
        # Math symbol mappings for normalization
        self.math_symbol_mappings = {
            # Greek letters
            'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ',
            'epsilon': 'ε', 'theta': 'θ', 'lambda': 'λ', 'mu': 'μ',
            'pi': 'π', 'sigma': 'σ', 'phi': 'φ', 'omega': 'ω',
            
            # Mathematical operators
            'infinity': '∞', 'infty': '∞',
            'sqrt': '√', 'cbrt': '∛',
            'integral': '∫', 'sum': '∑', 'product': '∏',
            'partial': '∂', 'nabla': '∇',
            
            # Relations
            'leq': '≤', 'geq': '≥', 'neq': '≠', 'approx': '≈',
            'equiv': '≡', 'propto': '∝',
            
            # Set theory
            'in': '∈', 'notin': '∉', 'subset': '⊂', 'supset': '⊃',
            'cup': '∪', 'cap': '∩', 'emptyset': '∅',
            
            # Logic
            'and': '∧', 'or': '∨', 'not': '¬', 'implies': '⇒',
            'iff': '⇔', 'forall': '∀', 'exists': '∃',
        }
        
        # Common math patterns
        self.math_patterns = [
            r'\b\d+\s*[+\-*/^]\s*\d+',  # Basic arithmetic
            r'[a-zA-Z]\s*[=<>≤≥≠]\s*[a-zA-Z0-9]',  # Variables/equations
            r'\\[a-zA-Z]+\{.*?\}',  # LaTeX commands
            r'\b(?:sin|cos|tan|log|ln|exp|sqrt)\s*\(',  # Functions
            r'\b(?:lim|int|sum|prod)\s*',  # Calculus operations
            r'\b(?:find|solve|calculate|prove|show)\b',  # Math verbs
        ]
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize input text for mathematical processing
        
        Args:
            text: Input text string
            
        Returns:
            Normalized text
        """
        try:
            # Unicode normalization
            normalized = unicodedata.normalize('NFKC', text)
            
            # Remove extra whitespace
            normalized = re.sub(r'\s+', ' ', normalized)
            
            # Convert math symbols
            normalized = self.convert_math_symbols(normalized)
            
            # Fix common formatting issues
            normalized = self.fix_formatting(normalized)
            
            return normalized.strip()
            
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            return text
    
    def convert_math_symbols(self, text: str) -> str:
        """
        Convert text representations to mathematical symbols
        
        Args:
            text: Input text
            
        Returns:
            Text with converted symbols
        """
        result = text
        
        # Convert word representations to symbols
        for word, symbol in self.math_symbol_mappings.items():
            pattern = r'\b' + re.escape(word) + r'\b'
            result = re.sub(pattern, symbol, result, flags=re.IGNORECASE)
        
        # Handle special cases
        result = self.handle_special_patterns(result)
        
        return result
    
    def handle_special_patterns(self, text: str) -> str:
        """
        Handle special mathematical patterns in text
        
        Args:
            text: Input text
            
        Returns:
            Text with handled patterns
        """
        # Handle fractions: "a/b" or "a over b"
        text = re.sub(r'(\w+)\s+over\s+(\w+)', r'(\1)/(\2)', text)
        
        # Handle exponents: "x^2" or "x to the power of 2"
        text = re.sub(r'(\w+)\s+to\s+the\s+power\s+of\s+(\w+)', r'\1^(\2)', text)
        text = re.sub(r'(\w+)\s+squared', r'\1²', text)
        text = re.sub(r'(\w+)\s+cubed', r'\1³', text)
        
        # Handle square roots: "sqrt(x)" or "square root of x"
        text = re.sub(r'square\s+root\s+of\s+(\w+)', r'√(\1)', text)
        
        # Handle absolute value: "|x|" or "absolute value of x"
        text = re.sub(r'absolute\s+value\s+of\s+(\w+)', r'|\1|', text)
        
        # Handle derivatives: "derivative of f with respect to x"
        text = re.sub(r'derivative\s+of\s+(\w+)\s+with\s+respect\s+to\s+(\w+)', r'd(\1)/d(\2)', text)
        
        # Handle limits: "limit as x approaches a"
        text = re.sub(r'limit\s+as\s+(\w+)\s+approaches\s+(\w+)', r'lim_{(\1)→(\2)}', text)
        
        return text
    
    def fix_formatting(self, text: str) -> str:
        """
        Fix common formatting issues in mathematical text
        
        Args:
            text: Input text
            
        Returns:
            Text with fixed formatting
        """
        # Fix spacing around operators
        text = re.sub(r'([+\-*/=<>≤≥≠])', r' \1 ', text)
        text = re.sub(r'\s+([+\-*/=<>≤≥≠])\s+', r' \1 ', text)
        
        # Fix parentheses spacing
        text = re.sub(r'\s*\(\s*', '(', text)
        text = re.sub(r'\s*\)\s*', ')', text)
        
        # Fix number formatting
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)  # Remove spaces within numbers
        text = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', text)  # Fix decimal points
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_math_components(self, text: str) -> Dict[str, Any]:
        """
        Extract mathematical components from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing extracted components
        """
        components = {
            "variables": [],
            "constants": [],
            "operators": [],
            "functions": [],
            "equations": [],
            "mathematical_context": False
        }
        
        try:
            # Extract variables (single letters, possibly with subscripts)
            variables = re.findall(r'\b[a-zA-Z]\b|\b[a-zA-Z]_\w+', text)
            components["variables"] = list(set(variables))
            
            # Extract constants (numbers, pi, e, etc.)
            constants = re.findall(r'\b\d+\.?\d*\b|π|e|∞', text)
            components["constants"] = list(set(constants))
            
            # Extract operators
            operators = re.findall(r'[+\-*/^=<>≤≥≠≈±∓√∫∑∏∂∇]', text)
            components["operators"] = list(set(operators))
            
            # Extract functions
            functions = re.findall(r'\b(?:sin|cos|tan|sec|csc|cot|arcsin|arccos|arctan|sinh|cosh|tanh|log|ln|exp|sqrt|abs|floor|ceil|round)\b', text, re.IGNORECASE)
            components["functions"] = list(set(functions))
            
            # Extract equations (expressions with =)
            equations = re.findall(r'[^=]*=[^=]*', text)
            components["equations"] = equations
            
            # Determine if text has mathematical context
            components["mathematical_context"] = self.is_mathematical_text(text)
            
            return components
            
        except Exception as e:
            logger.error(f"Math component extraction failed: {str(e)}")
            return components
    
    def is_mathematical_text(self, text: str) -> bool:
        """
        Determine if text contains mathematical content
        
        Args:
            text: Input text
            
        Returns:
            True if text appears to be mathematical
        """
        # Check for mathematical patterns
        pattern_matches = sum(1 for pattern in self.math_patterns 
                             if re.search(pattern, text, re.IGNORECASE))
        
        # Check for mathematical symbols
        math_symbols = re.findall(r'[+\-*/^=<>≤≥≠≈±∓√∫∑∏∂∇π∞αβγδεθλμσφω]', text)
        
        # Check for mathematical keywords
        math_keywords = ['solve', 'find', 'calculate', 'prove', 'show', 'derive', 
                        'simplify', 'evaluate', 'integrate', 'differentiate',
                        'equation', 'function', 'variable', 'coefficient', 'polynomial']
        
        keyword_matches = sum(1 for keyword in math_keywords 
                             if keyword.lower() in text.lower())
        
        # Scoring system
        score = pattern_matches * 2 + len(math_symbols) + keyword_matches
        
        return score >= 3
    
    def validate_text_input(self, text: str) -> Dict[str, Any]:
        """
        Validate text input for mathematical processing
        
        Args:
            text: Input text
            
        Returns:
            Validation result
        """
        validation = {
            "is_valid": False,
            "is_mathematical": False,
            "text_length_adequate": False,
            "contains_special_chars": False,
            "encoding_issues": False,
            "recommendations": []
        }
        
        try:
            # Check text length
            validation["text_length_adequate"] = len(text.strip()) >= 3
            
            # Check mathematical content
            validation["is_mathematical"] = self.is_mathematical_text(text)
            
            # Check for special characters
            validation["contains_special_chars"] = bool(re.search(r'[^\w\s+\-*/^=<>()[\]{}.,!?;:]', text))
            
            # Check for encoding issues
            try:
                text.encode('utf-8').decode('utf-8')
                validation["encoding_issues"] = False
            except UnicodeError:
                validation["encoding_issues"] = True
            
            # Overall validation
            validation["is_valid"] = all([
                validation["text_length_adequate"],
                validation["is_mathematical"],
                not validation["encoding_issues"]
            ])
            
            # Generate recommendations
            if not validation["text_length_adequate"]:
                validation["recommendations"].append("Text too short - provide more context")
            
            if not validation["is_mathematical"]:
                validation["recommendations"].append("Text doesn't appear to contain mathematical content")
            
            if validation["encoding_issues"]:
                validation["recommendations"].append("Text contains encoding issues - check special characters")
            
            return validation
            
        except Exception as e:
            logger.error(f"Text validation failed: {str(e)}")
            validation["recommendations"].append(f"Validation error: {str(e)}")
            return validation
    
    def process_text_input(self, text: str) -> Dict[str, Any]:
        """
        Process text input and return normalized text with metadata
        
        Args:
            text: Input text string
            
        Returns:
            Processing results
        """
        try:
            # Normalize text
            normalized_text = self.normalize_text(text)
            
            # Extract mathematical components
            components = self.extract_math_components(normalized_text)
            
            # Validate input
            validation = self.validate_text_input(normalized_text)
            
            return {
                "original_text": text,
                "normalized_text": normalized_text,
                "components": components,
                "validation": validation,
                "text_length": len(text),
                "processing_successful": True,
                "needs_human_review": not validation["is_valid"],
                "confidence": 1.0 if validation["is_valid"] else 0.5
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {str(e)}")
            return {
                "original_text": text,
                "normalized_text": text,
                "components": {},
                "validation": {"is_valid": False, "recommendations": [f"Processing failed: {str(e)}"]},
                "text_length": len(text),
                "processing_successful": False,
                "needs_human_review": True,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def clean_latex(self, text: str) -> str:
        """
        Clean and normalize LaTeX mathematical expressions
        
        Args:
            text: Text that may contain LaTeX
            
        Returns:
            Cleaned text
        """
        try:
            # Remove display math delimiters
            text = re.sub(r'\$\$([^$]+)\$\$', r'\1', text)
            
            # Remove inline math delimiters
            text = re.sub(r'\$([^$]+)\$', r'\1', text)
            
            # Convert common LaTeX commands
            latex_replacements = {
                r'\\frac\{([^}]+)\}\{([^}]+)\}': r'(\1)/(\2)',
                r'\\sqrt\{([^}]+)\}': r'√(\1)',
                r'\\sum_\{([^}]+)\}\^\{([^}]+)\}': r'∑(\1 to \2)',
                r'\\int_\{([^}]+)\}\^\{([^}]+)\}': r'∫(\1 to \2)',
                r'\\lim_\{([^}]+)\}': r'lim(\1)',
                r'\\infty': '∞',
                r'\\pi': 'π',
                r'\\theta': 'θ',
                r'\\alpha': 'α',
                r'\\beta': 'β',
                r'\\gamma': 'γ',
                r'\\delta': 'δ',
                r'\\epsilon': 'ε',
                r'\\lambda': 'λ',
                r'\\mu': 'μ',
                r'\\sigma': 'σ',
                r'\\phi': 'φ',
                r'\\omega': 'ω',
                r'\\leq': '≤',
                r'\\geq': '≥',
                r'\\neq': '≠',
                r'\\approx': '≈',
                r'\\equiv': '≡',
                r'\\partial': '∂',
                r'\\nabla': '∇',
                r'\\cdot': '·',
                r'\\times': '×',
                r'\\pm': '±',
                r'\\mp': '∓'
            }
            
            for pattern, replacement in latex_replacements.items():
                text = re.sub(pattern, replacement, text)
            
            # Remove remaining LaTeX commands
            text = re.sub(r'\\[a-zA-Z]+\{?([^}]*)\}?', r'\1', text)
            
            # Clean up formatting
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"LaTeX cleaning failed: {str(e)}")
            return text