# -*- coding: utf-8 -*-
"""
Audio Processor for Math Mentor AI
Handles audio recording, file upload, and speech-to-text conversion
Professional implementation with HITL workflow and Windows compatibility
"""

import os
import io
import logging
import tempfile
import time
import platform
import atexit
import glob
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Configure ffmpeg PATH for Windows before importing audio libraries
if platform.system() == "Windows":
    # Search for ffmpeg in WinGet installation location
    localappdata = os.environ.get('LOCALAPPDATA', '')
    ffmpeg_pattern = os.path.join(localappdata, 'Microsoft', 'WinGet', 'Packages', 
                                   'Gyan.FFmpeg*', 'ffmpeg*', 'bin')
    
    matches = glob.glob(ffmpeg_pattern)
    if matches:
        ffmpeg_bin_dir = matches[0]
        if os.path.exists(ffmpeg_bin_dir):
            # Add ffmpeg to PATH for this process
            os.environ['PATH'] = ffmpeg_bin_dir + os.pathsep + os.environ.get('PATH', '')
            print(f"Added ffmpeg to PATH: {ffmpeg_bin_dir}")

logger = logging.getLogger(__name__)

# Enable Whisper for speech-to-text functionality (per task guide)
WHISPER_AVAILABLE = False
try:
    import whisper
    WHISPER_AVAILABLE = True
    logger.info("OpenAI Whisper loaded successfully")
except ImportError:
    logger.warning("Whisper not available - install with: pip install openai-whisper")

# Enable audio conversion for multimodal processing  
PYDUB_AVAILABLE = False
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
    logger.info("Pydub loaded successfully for audio conversion")
except ImportError:
    logger.warning("Pydub not available - install with: pip install pydub")

# Try to import pyaudio for recording (optional)
PYAUDIO_AVAILABLE = False
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    logger.info("PyAudio loaded successfully")
except ImportError:
    logger.warning("PyAudio not available - install with: pip install pyaudio")

# Audio format support
SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.webm', '.ogg', '.flac', '.opus']


class AudioProcessor:
    """
    Professional audio processor with speech-to-text capabilities
    Supports: recording, file upload, Whisper transcription, HITL workflow
    """
    
    def __init__(self):
        """Initialize audio processor with Whisper model"""
        self.whisper_model = None
        self.whisper_available = WHISPER_AVAILABLE
        self.temp_files = []  # Track temp files for cleanup
        
        # Load Whisper model - 'base' for fast real-time transcription
        if self.whisper_available:
            try:
                logger.info("Loading Whisper base model...")
                self.whisper_model = whisper.load_model("base")
                logger.info("Whisper base model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                self.whisper_available = False
        
        # Register cleanup on exit
        atexit.register(self._cleanup_temp_files)
    
    def process_audio_input(self, audio_input: Union[Dict, bytes, io.BytesIO, str, Path], 
                           **kwargs) -> Dict[str, Any]:
        """
        Process audio from recording or uploaded file (input coordinator compatible)
        
        Args:
            audio_input: Audio bytes, BytesIO, file path, or dict with 'audio_file' key
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with transcription results in standardized format
        """
        try:
            # Handle dict input from coordinator
            if isinstance(audio_input, dict):
                audio_data = audio_input.get('audio_file') or audio_input.get('audio_bytes')
                if not audio_data:
                    return self._create_error_result('No audio data provided in input dict')
            else:
                audio_data = audio_input
            
            # Process the audio
            result = self.process_audio(audio_data, **kwargs)
            
            # Convert to coordinator-expected format
            return self._format_for_coordinator(result)
            
        except Exception as e:
            logger.error(f"Audio input processing error: {e}")
            return self._create_error_result(str(e))
    
    def process_audio(self, audio_input: Union[bytes, io.BytesIO, str, Path], 
                     **kwargs) -> Dict[str, Any]:
        """
        Process audio from recording or uploaded file
        
        Args:
            audio_input: Audio bytes, BytesIO, or file path
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with transcription results and metadata
        """
        try:
            logger.info(f"Processing audio input of type: {type(audio_input)}")
            
            # Validate Whisper availability
            if not self.whisper_available or not self.whisper_model:
                error_msg = 'Whisper not available. Install with: pip install openai-whisper'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'text': '',
                    'confidence': 0.0,
                    'needs_human_review': True
                }
            
            # Convert input to file path
            audio_path = self._prepare_audio_file(audio_input)
            if not audio_path:
                error_msg = 'Failed to prepare audio file - check if audio data is valid'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'text': '',
                    'confidence': 0.0,
                    'needs_human_review': True
                }
            
            logger.info(f"Audio file prepared: {audio_path}")
            
            # Verify file exists before transcription
            if not os.path.exists(audio_path):
                error_msg = f'Audio file does not exist: {audio_path}'
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': 'Audio file not found - please record again',
                    'text': '',
                    'confidence': 0.0,
                    'needs_human_review': True
                }
            
            # Small delay on Windows to ensure file is fully accessible
            if platform.system() == "Windows":
                time.sleep(0.1)  # Minimal delay for file sync
            
            # Quick file access check
            if not os.access(audio_path, os.R_OK):
                logger.error(f'Audio file not accessible')
                return {
                    'success': False,
                    'error': 'Audio file cannot be read - please try again',
                    'text': '',
                    'confidence': 0.0,
                    'needs_human_review': True
                }
            
            # Transcribe with Whisper
            result = self._transcribe_with_whisper(audio_path)
            
            # Cleanup temp file
            self._safe_cleanup(audio_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': self._format_error_message(str(e)),
                'text': '',
                'confidence': 0.0,
                'needs_human_review': True
            }
    
    def _prepare_audio_file(self, audio_input: Union[bytes, io.BytesIO, str, Path]) -> Optional[str]:
        """
        Prepare audio file for Whisper (Windows-compatible)
        
        Args:
            audio_input: Audio data in various formats
            
        Returns:
            Path to temporary audio file or None if failed
        """
        try:
            # Handle BytesIO
            if isinstance(audio_input, io.BytesIO):
                # Seek to beginning in case BytesIO was already read
                audio_input.seek(0)
                audio_bytes = audio_input.getvalue()
                if not audio_bytes or len(audio_bytes) == 0:
                    logger.error("BytesIO object contains no data")
                    return None
                return self._save_bytes_to_temp_file(audio_bytes)
            
            # Handle raw bytes
            elif isinstance(audio_input, bytes):
                if not audio_input or len(audio_input) == 0:
                    logger.error("Empty bytes provided")
                    return None
                return self._save_bytes_to_temp_file(audio_input)
            
            # Handle file path
            elif isinstance(audio_input, (str, Path)):
                path = Path(audio_input)
                if path.exists() and path.is_file():
                    return str(path)
                else:
                    logger.error(f"Audio file not found: {path}")
                    return None
            
            # Handle file-like objects
            elif hasattr(audio_input, 'read'):
                # Seek to beginning if possible
                if hasattr(audio_input, 'seek'):
                    try:
                        audio_input.seek(0)
                    except:
                        pass  # Some file-like objects don't support seek
                
                audio_bytes = audio_input.read()
                if not audio_bytes or len(audio_bytes) == 0:
                    logger.error("File-like object contains no data")
                    return None
                return self._save_bytes_to_temp_file(audio_bytes)
            
            else:
                logger.error(f"Unsupported audio input type: {type(audio_input)}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to prepare audio file: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return None
    
    def _save_bytes_to_temp_file(self, audio_bytes: bytes) -> Optional[str]:
        """
        Save audio bytes to temporary file (Windows-compatible method)
        Uses mkstemp() instead of NamedTemporaryFile for proper Windows support
        
        Args:
            audio_bytes: Raw audio data
            
        Returns:
            Path to temporary file or None if failed
        """
        temp_path = None
        fd = None
        
        try:
            # Validate input
            if not audio_bytes:
                logger.error("No audio bytes provided (None)")
                return None
            
            if len(audio_bytes) == 0:
                logger.error("Empty audio bytes provided (0 length)")
                return None
            
            # Quick format detection
            if len(audio_bytes) >= 4:
                first_bytes = audio_bytes[:4].hex()
                is_webm = first_bytes.startswith('1a45dfa3')
                is_wav = first_bytes.startswith('52494646')
                is_mp3 = audio_bytes[:3].hex().startswith('494433') or audio_bytes[:2].hex().startswith('fffb')
                
                # If it's not a known format, treat as raw PCM (fast conversion)
                if not (is_webm or is_wav or is_mp3):
                    try:
                        import numpy as np
                        import soundfile as sf
                        
                        # Convert as 16-bit PCM
                        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                        
                        # Quick silence check
                        max_amp = np.max(np.abs(audio_array))
                        if max_amp == 0:
                            logger.error("Silent audio detected")
                            return None
                        
                        # Normalize if too quiet (fast threshold check)
                        if max_amp < 1000:
                            audio_array = (audio_array.astype(np.float32) / max_amp * 30000).astype(np.int16)
                        
                        # Create WAV file
                        wav_fd, wav_path = tempfile.mkstemp(suffix=".wav", prefix="audio_")
                        os.close(wav_fd)
                        sf.write(wav_path, audio_array, 16000)
                        
                        self.temp_files.append(wav_path)
                        return wav_path
                        
                    except Exception as e:
                        logger.error(f"PCM conversion failed: {e}")
                        return None
            
            # Use mkstemp for Windows compatibility
            fd, temp_path = tempfile.mkstemp(suffix=".webm", prefix="audio_")
            
            # Write data using file descriptor
            os.write(fd, audio_bytes)
            os.fsync(fd)
            os.close(fd)
            fd = None
            
            # Quick validation
            file_size = os.path.getsize(temp_path)
            if file_size == 0:
                logger.error(f"Empty temp file")
                os.unlink(temp_path)
                return None
            
            # Fast WebM to WAV conversion if needed
            if PYDUB_AVAILABLE and temp_path.endswith('.webm'):
                try:
                    audio_segment = AudioSegment.from_file(temp_path, format="webm")
                    wav_fd, wav_path = tempfile.mkstemp(suffix=".wav", prefix="audio_")
                    os.close(wav_fd)
                    audio_segment.export(wav_path, format="wav")
                    
                    try:
                        os.unlink(temp_path)
                        self.temp_files.remove(temp_path)
                    except:
                        pass
                    
                    temp_path = wav_path
                    file_size = os.path.getsize(temp_path)
                except Exception as conv_err:
                    logger.warning(f"Conversion failed: {conv_err}")
            
            # Track for cleanup
            self.temp_files.append(temp_path)
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to save audio bytes: {e}")
            import traceback
            logger.debug(f"Traceback: {traceback.format_exc()}")
            
            # Cleanup on error
            if fd is not None:
                try:
                    os.close(fd)
                except:
                    pass
            
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            return None
    
    def _transcribe_with_whisper(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe audio using OpenAI Whisper with optimized parameters
        
        Args:
            audio_path: Path to audio file (preferably WAV)
            
        Returns:
            Transcription result with confidence and HITL indicators
        """
        try:
            # Quick validation
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
                raise ValueError("Invalid audio file")
            
            # Ultra-fast transcription with noise tolerance
            result = self.whisper_model.transcribe(
                audio_path,
                language='en',
                fp16=False,
                best_of=1,
                beam_size=1,
                temperature=0.0,
                no_speech_threshold=0.2,
                logprob_threshold=-0.8,
                compression_ratio_threshold=2.8,
                condition_on_previous_text=False,
                verbose=False
            )
            
            # Extract text and segments
            text = result.get('text', '').strip()
            segments = result.get('segments', [])
            language = result.get('language', 'en')
            
            # Calculate confidence from segments
            confidence = self._calculate_confidence(segments)
            
            # Determine if human review is needed
            needs_review = self._needs_human_review(text, confidence, result)
            
            # Check for no speech detected
            if not text or len(text) < 2:
                return {
                    'success': False,
                    'error': 'No speech detected',
                    'text': '',
                    'confidence': 0.0,
                    'needs_human_review': True
                }
            
            logger.info(f"Transcribed: {len(text)} chars (confidence: {confidence:.2f})")
            
            return {
                'success': True,
                'text': text,
                'original_text': text,
                'enhanced_text': text,  # Could add enhancement later
                'confidence': confidence,
                'needs_human_review': needs_review,
                'language': language,
                'segments': segments,
                'word_count': len(text.split()),
                'duration': result.get('duration', 0),
                'whisper_result': result
            }
            
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {
                'success': False,
                'error': self._format_error_message(str(e)),
                'text': '',
                'confidence': 0.0,
                'needs_human_review': True
            }
    
    def _calculate_confidence(self, segments: list) -> float:
        """
        Calculate overall confidence from Whisper segments
        
        Args:
            segments: Whisper segment data
            
        Returns:
            Confidence score (0.0-100.0)
        """
        if not segments:
            return 0.0
        
        try:
            # Average the probability/confidence from segments
            confidences = []
            for segment in segments:
                # Whisper provides average log probability
                avg_logprob = segment.get('avg_logprob', -1.0)
                # Convert log probability to confidence (0-1)
                # logprob ranges from -inf to 0, we normalize to 0-1
                confidence = min(1.0, max(0.0, 1.0 + (avg_logprob / 1.0)))
                confidences.append(confidence)
            
            # Average confidence across all segments
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                return avg_confidence * 100.0  # Convert to percentage
            
            return 70.0  # Default moderate confidence
            
        except Exception as e:
            logger.warning(f"Failed to calculate confidence: {e}")
            return 70.0
    
    def _needs_human_review(self, text: str, confidence: float, 
                           whisper_result: dict) -> bool:
        """
        Determine if transcription needs human review (HITL)
        
        Args:
            text: Transcribed text
            confidence: Confidence score
            whisper_result: Full Whisper result
            
        Returns:
            True if human review recommended
        """
        # Low confidence threshold
        if confidence < 70.0:
            return True
        
        # Very short text (might be incomplete)
        if len(text.strip()) < 5:
            return True
        
        # Check Whisper's no_speech_prob
        no_speech_prob = whisper_result.get('no_speech_prob', 0.0)
        if no_speech_prob > 0.5:
            return True
        
        # Otherwise, seems reliable
        return False
    
    def _safe_cleanup(self, file_path: str):
        """
        Safely cleanup temporary file with Windows compatibility
        
        Args:
            file_path: Path to file to delete
        """
        if not file_path or not os.path.exists(file_path):
            return
        
        try:
            # Windows-specific delay before cleanup
            if platform.system() == "Windows":
                time.sleep(0.2)
            
            os.unlink(file_path)
            
            # Remove from tracking list
            if file_path in self.temp_files:
                self.temp_files.remove(file_path)
            
            logger.debug(f"Cleaned up temp file: {file_path}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")
            # Register for deferred cleanup
            atexit.register(self._deferred_cleanup, file_path)
    
    def _deferred_cleanup(self, file_path: str):
        """Deferred cleanup for files that couldn't be deleted immediately"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.debug(f"Deferred cleanup successful: {file_path}")
        except:
            pass  # Silent fail on exit
    
    def _cleanup_temp_files(self):
        """Cleanup all tracked temporary files on exit"""
        for file_path in self.temp_files[:]:  # Copy list
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass
        self.temp_files.clear()
    
    def _format_error_message(self, error_str: str) -> str:
        """
        Format error messages to be user-friendly
        
        Args:
            error_str: Raw error message
            
        Returns:
            User-friendly error message
        """
        # Windows file access errors
        if "WinError 32" in error_str:
            return "File access error - please try recording again"
        
        if "WinError 2" in error_str or "No such file" in error_str:
            return "Audio file not found - please record again"
        
        # Whisper errors
        if "Whisper" in error_str or "whisper" in error_str:
            return "Speech recognition engine error. Please ensure Whisper is installed: pip install openai-whisper"
        
        if "ffmpeg" in error_str.lower():
            return "FFmpeg not found. Please install FFmpeg and add to PATH"
        
        # Model errors
        if "model" in error_str.lower():
            return "Speech recognition model error - please try again"
        
        # Generic audio errors
        if "audio" in error_str.lower():
            return f"Audio processing error: {error_str[:100]}"
        
        # Return shortened error
        return error_str[:150]
    
    def _format_for_coordinator(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format result for input coordinator compatibility
        
        Args:
            result: Raw audio processing result
            
        Returns:
            Coordinator-compatible result
        """
        return {
            'processing_successful': result.get('success', False),
            'text': result.get('text', ''),
            'original_text': result.get('original_text', result.get('text', '')),
            'enhanced_text': result.get('enhanced_text', result.get('text', '')),
            'overall_confidence': result.get('confidence', 0.0),
            'needs_human_review': result.get('needs_human_review', True),
            'language': result.get('language', 'en'),
            'segments': result.get('segments', []),
            'model': 'whisper-base',
            'validation': {
                'is_valid': result.get('success', False),
                'recommendations': []
            },
            'error': result.get('error', None)
        }
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error result
        
        Args:
            error_message: Error description
            
        Returns:
            Error result in coordinator format
        """
        return {
            'processing_successful': False,
            'text': '',
            'original_text': '',
            'enhanced_text': '',
            'overall_confidence': 0.0,
            'needs_human_review': True,
            'language': 'en',
            'segments': [],
            'model': 'whisper-base',
            'validation': {
                'is_valid': False,
                'recommendations': ['Fix audio processing error']
            },
            'error': self._format_error_message(error_message)
        }
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return SUPPORTED_FORMATS.copy()
    
    def is_available(self) -> bool:
        """Check if audio processing is available"""
        return self.whisper_available and self.whisper_model is not None
    
    def get_info(self) -> Dict[str, Any]:
        """Get processor information"""
        return {
            'whisper_available': self.whisper_available,
            'model_loaded': self.whisper_model is not None,
            'supported_formats': self.get_supported_formats(),
            'platform': platform.system()
        }
