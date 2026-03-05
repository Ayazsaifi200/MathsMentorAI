# -*- coding: utf-8 -*-
"""
Input Coordinator for Math Mentor AI
Coordinates multimodal input processing (text, image, audio)
"""

import logging
from typing import Dict, Any, Union, Optional
from enum import Enum
import numpy as np
from PIL import Image

from .text_processor import TextProcessor
from .ocr_processor import OCRProcessor
from .audio_processor import AudioProcessor

logger = logging.getLogger(__name__)

class InputType(Enum):
    """Enumeration for input types"""
    TEXT = "text"
    IMAGE = "image"  
    AUDIO = "audio"

class InputCoordinator:
    """Coordinator for handling multimodal input processing"""
    
    def __init__(self):
        """Initialize input coordinator with processors"""
        self.text_processor = TextProcessor()
        self.ocr_processor = OCRProcessor()
        self.audio_processor = AudioProcessor()
        
        logger.info("Input coordinator initialized with all processors")
    
    def process_input(self, 
                     input_data: Any, 
                     input_type: InputType, 
                     **kwargs) -> Dict[str, Any]:
        """
        Process input based on type
        
        Args:
            input_data: Input data (text, image, or audio)
            input_type: Type of input (InputType enum)
            **kwargs: Additional processing options
            
        Returns:
            Unified processing result
        """
        try:
            logger.info(f"Processing {input_type.value} input")
            
            if input_type == InputType.TEXT:
                result = self._process_text_input(input_data, **kwargs)
            elif input_type == InputType.IMAGE:
                result = self._process_image_input(input_data, **kwargs)
            elif input_type == InputType.AUDIO:
                result = self._process_audio_input(input_data, **kwargs)
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            # Add common metadata
            result.update({
                "input_type": input_type.value,
                "timestamp": self._get_timestamp(),
                "coordinator_version": "1.0"
            })
            
            # Standardize the result format
            standardized_result = self._standardize_result(result, input_type)
            
            logger.info(f"Input processing completed for {input_type.value}")
            return standardized_result
            
        except Exception as e:
            logger.error(f"Input processing failed for {input_type.value}: {str(e)}")
            return self._create_error_result(input_type, str(e))
    
    def _process_text_input(self, text: str, **kwargs) -> Dict[str, Any]:
        """Process text input"""
        return self.text_processor.process_text_input(text)
    
    def _process_image_input(self, image_data: Any, **kwargs) -> Dict[str, Any]:
        """Process image input"""
        return self.ocr_processor.process_image_input(image_data)
    
    def _process_audio_input(self, audio_data: Any, **kwargs) -> Dict[str, Any]:
        """Process audio input"""
        return self.audio_processor.process_audio_input(audio_data)
    
    def _standardize_result(self, result: Dict[str, Any], input_type: InputType) -> Dict[str, Any]:
        """
        Standardize processing results across all input types
        
        Args:
            result: Raw processing result
            input_type: Type of input processed
            
        Returns:
            Standardized result format
        """
        standardized = {
            # Core fields
            "extracted_text": "",
            "confidence": 0.0,
            "needs_human_review": True,
            "processing_successful": False,
            
            # Input-specific data
            "raw_result": result,
            "input_metadata": {},
            
            # Validation and quality
            "validation": {"is_valid": False, "recommendations": []},
            "quality_metrics": {},
            
            # HITL trigger information
            "hitl_triggers": [],
            "suggested_actions": []
        }
        
        try:
            if input_type == InputType.TEXT:
                standardized.update({
                    "extracted_text": result.get("normalized_text", ""),
                    "confidence": result.get("confidence", 0.0),
                    "needs_human_review": result.get("needs_human_review", True),
                    "processing_successful": result.get("processing_successful", False),
                    "validation": result.get("validation", {}),
                    "input_metadata": {
                        "original_text": result.get("original_text", ""),
                        "text_length": result.get("text_length", 0),
                        "components": result.get("components", {})
                    }
                })
                
            elif input_type == InputType.IMAGE:
                # Get data from raw_result (contains actual OCR data)
                raw_result = result.get("raw_result", {})
                extracted_text = result.get("text", "")
                # Confidence is now normalized in OCR processor (handles both formats)
                confidence = raw_result.get("confidence", 0.0)
                processing_successful = result.get("success", False)
                
                standardized.update({
                    "extracted_text": extracted_text,
                    "confidence": confidence,
                    "needs_human_review": confidence < 85.0,
                    "processing_successful": processing_successful,
                    "input_metadata": {
                        "image_shape": raw_result.get("image_shape", None),
                        "word_confidences": raw_result.get("word_confidences", []),
                        "ocr_method": raw_result.get("method", "tesseract"),
                        "comparison": raw_result.get("comparison", {})
                    },
                    "quality_metrics": {
                        "ocr_confidence": confidence,
                        "word_count": len(extracted_text.split()) if extracted_text else 0
                    }
                })
                
            elif input_type == InputType.AUDIO:
                standardized.update({
                    "extracted_text": result.get("text", ""),
                    "confidence": result.get("overall_confidence", 0.0),
                    "needs_human_review": result.get("needs_human_review", True),
                    "processing_successful": result.get("processing_successful", False),
                    "validation": result.get("validation", {}),
                    "input_metadata": {
                        "language": result.get("language", "unknown"),
                        "segments": result.get("segments", []),
                        "enhanced_text": result.get("enhanced_text", ""),
                        "original_text": result.get("original_text", ""),
                        "model_used": result.get("model", "whisper-base")
                    },
                    "quality_metrics": {
                        "transcription_confidence": result.get("overall_confidence", 0.0),
                        "segment_count": len(result.get("segments", []))
                    }
                })
            
            # Generate HITL triggers
            standardized["hitl_triggers"] = self._identify_hitl_triggers(standardized, input_type)
            
            # Generate suggested actions
            standardized["suggested_actions"] = self._generate_suggested_actions(standardized, input_type)
            
        except Exception as e:
            logger.error(f"Result standardization failed: {str(e)}")
            standardized["error"] = str(e)
        
        return standardized
    
    def _identify_hitl_triggers(self, result: Dict[str, Any], input_type: InputType) -> list:
        """
        Identify conditions that should trigger human-in-the-loop review
        
        Args:
            result: Standardized processing result
            input_type: Type of input processed
            
        Returns:
            List of HITL trigger reasons
        """
        triggers = []
        
        try:
            # Low confidence trigger
            if result["confidence"] < 60.0:  # threshold in percentage
                triggers.append({
                    "type": "low_confidence",
                    "reason": f"Confidence {result['confidence']:.1f}% is below threshold",
                    "severity": "high" if result["confidence"] < 40.0 else "medium"
                })
            
            # Processing failure trigger
            if not result["processing_successful"]:
                triggers.append({
                    "type": "processing_failure",
                    "reason": "Processing was not successful",
                    "severity": "high"
                })
            
            # Validation failure trigger
            validation = result.get("validation", {})
            if not validation.get("is_valid", False):
                triggers.append({
                    "type": "validation_failure", 
                    "reason": "Input validation failed",
                    "severity": "medium",
                    "recommendations": validation.get("recommendations", [])
                })
            
            # Input-specific triggers
            if input_type == InputType.IMAGE:
                # OCR-specific triggers
                word_confidences = result["input_metadata"].get("word_confidences", [])
                if word_confidences and min(word_confidences) < 30:
                    triggers.append({
                        "type": "low_word_confidence",
                        "reason": "Some words have very low OCR confidence",
                        "severity": "medium"
                    })
                
                # Short text trigger for images
                if len(result["extracted_text"].strip()) < 10:
                    triggers.append({
                        "type": "insufficient_text",
                        "reason": "Very little text extracted from image",
                        "severity": "medium"
                    })
            
            elif input_type == InputType.AUDIO:
                # Language detection trigger
                language = result["input_metadata"].get("language", "unknown") 
                if language not in ["en", "english"]:
                    triggers.append({
                        "type": "language_uncertainty",
                        "reason": f"Detected language '{language}' may affect accuracy",
                        "severity": "low"
                    })
                
                # No mathematical content trigger
                validation = result.get("validation", {})
                if not validation.get("contains_math", True):
                    triggers.append({
                        "type": "no_math_content",
                        "reason": "No mathematical content detected in transcription",
                        "severity": "medium"
                    })
        
        except Exception as e:
            logger.error(f"HITL trigger identification failed: {str(e)}")
            triggers.append({
                "type": "trigger_identification_error",
                "reason": f"Error identifying triggers: {str(e)}",
                "severity": "low"
            })
        
        return triggers
    
    def _generate_suggested_actions(self, result: Dict[str, Any], input_type: InputType) -> list:
        """
        Generate suggested actions based on processing results
        
        Args:
            result: Standardized processing result
            input_type: Type of input processed
            
        Returns:
            List of suggested actions
        """
        actions = []
        
        try:
            # Based on HITL triggers
            for trigger in result.get("hitl_triggers", []):
                trigger_type = trigger.get("type")
                
                if trigger_type == "low_confidence":
                    if input_type == InputType.IMAGE:
                        actions.append({
                            "action": "retake_image",
                            "description": "Consider retaking the image with better lighting/focus",
                            "priority": "high"
                        })
                    elif input_type == InputType.AUDIO:
                        actions.append({
                            "action": "re_record_audio",
                            "description": "Consider re-recording in a quieter environment",
                            "priority": "high"
                        })
                
                elif trigger_type == "validation_failure":
                    actions.append({
                        "action": "manual_correction",
                        "description": "Manually review and correct the extracted text",
                        "priority": "medium"
                    })
                
                elif trigger_type == "insufficient_text":
                    actions.append({
                        "action": "crop_and_retry",
                        "description": "Crop the image to focus on the math problem and retry",
                        "priority": "medium"
                    })
            
            # General actions based on success
            if result["processing_successful"] and result["confidence"] > 80.0:
                actions.append({
                    "action": "proceed_to_parsing",
                    "description": "Processing successful - ready for mathematical parsing",
                    "priority": "low"
                })
            
            # If no specific actions, provide default
            if not actions:
                actions.append({
                    "action": "human_review",
                    "description": "Review extracted text before proceeding",
                    "priority": "medium"
                })
                
        except Exception as e:
            logger.error(f"Action generation failed: {str(e)}")
            actions.append({
                "action": "error_recovery",
                "description": f"Resolve processing issue: {str(e)}",
                "priority": "high"
            })
        
        return actions
    
    def _create_error_result(self, input_type: InputType, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error result
        
        Args:
            input_type: Type of input that failed
            error_message: Error description
            
        Returns:
            Standardized error result
        """
        return {
            "extracted_text": "",
            "confidence": 0.0,
            "needs_human_review": True,
            "processing_successful": False,
            "input_type": input_type.value,
            "error": error_message,
            "timestamp": self._get_timestamp(),
            "validation": {
                "is_valid": False,
                "recommendations": ["Processing failed - manual intervention required"]
            },
            "hitl_triggers": [{
                "type": "processing_error",
                "reason": error_message,
                "severity": "high"
            }],
            "suggested_actions": [{
                "action": "retry_or_manual",
                "description": "Retry processing or enter text manually",
                "priority": "high"
            }]
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """
        Get information about processing capabilities
        
        Returns:
            Dictionary describing processor capabilities
        """
        return {
            "supported_input_types": [t.value for t in InputType],
            "text_processing": {
                "normalization": True,
                "latex_support": True,
                "math_symbol_conversion": True,
                "component_extraction": True
            },
            "image_processing": {
                "ocr_engine": "tesseract",
                "preprocessing": True,
                "confidence_scoring": True,
                "math_optimized": True
            },
            "audio_processing": {
                "asr_engine": "whisper",
                "model": self.audio_processor.model_name,
                "math_vocabulary": True,
                "confidence_scoring": True
            },
            "hitl_integration": {
                "automatic_triggers": True,
                "confidence_thresholding": True,
                "suggested_actions": True
            }
        }
    
    def validate_input_format(self, input_data: Any, input_type: InputType) -> Dict[str, Any]:
        """
        Validate input format before processing
        
        Args:
            input_data: Input data to validate
            input_type: Expected input type
            
        Returns:
            Validation result
        """
        validation = {
            "is_valid": False,
            "format_correct": False,
            "size_acceptable": False,
            "recommendations": []
        }
        
        try:
            if input_type == InputType.TEXT:
                validation["format_correct"] = isinstance(input_data, str)
                validation["size_acceptable"] = 0 < len(input_data) < 10000  # reasonable text length
                
            elif input_type == InputType.IMAGE:
                if isinstance(input_data, str):
                    # File path
                    import os
                    validation["format_correct"] = os.path.exists(input_data)
                    if validation["format_correct"]:
                        validation["size_acceptable"] = os.path.getsize(input_data) < 10 * 1024 * 1024  # 10MB
                elif isinstance(input_data, (Image.Image, np.ndarray)):
                    validation["format_correct"] = True
                    validation["size_acceptable"] = True
                
            elif input_type == InputType.AUDIO:
                if isinstance(input_data, str):
                    # File path
                    import os
                    validation["format_correct"] = os.path.exists(input_data)
                    if validation["format_correct"]:
                        validation["size_acceptable"] = os.path.getsize(input_data) < 100 * 1024 * 1024  # 100MB
                elif isinstance(input_data, np.ndarray):
                    validation["format_correct"] = True
                    validation["size_acceptable"] = len(input_data) < 16000 * 300  # 5 minutes at 16kHz
            
            validation["is_valid"] = validation["format_correct"] and validation["size_acceptable"]
            
            # Generate recommendations
            if not validation["format_correct"]:
                validation["recommendations"].append(f"Invalid format for {input_type.value} input")
            
            if not validation["size_acceptable"]:
                validation["recommendations"].append(f"Input size too large for {input_type.value}")
                
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            validation["recommendations"].append(f"Validation error: {str(e)}")
        
        return validation