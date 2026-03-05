# -*- coding: utf-8 -*-
"""
Guardrail Agent for Math Mentor AI
Uses LLM to ensure safe and appropriate interactions
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class GuardrailAgent(BaseAgent):
    """AI-powered agent for safety and appropriateness checking"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define guardrail agent capabilities"""
        return AgentCapability(
            name="GuardrailAgent",
            description="Use AI to ensure safe and appropriate educational interactions",
            input_types=["any"],
            output_types=["safety_check"],
            dependencies=[],
            confidence_threshold=0.9
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to check for safety and appropriateness
        
        Args:
            input_data: Contains user input or content to check
            
        Returns:
            Safety assessment
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        content = input_data.get("content", "") or input_data.get("problem_text", "")
        
        # Use LLM for safety checking
        if self.llm_available:
            safety_result = self._check_with_ai(content)
        else:
            safety_result = self._basic_check(content)
        
        return self.create_success_response(safety_result)
    
    def _check_with_ai(self, content: str) -> Dict[str, Any]:
        """Use AI to check content safety"""
        
        prompt = f"""You are a safety moderator for an educational mathematics platform for JEE students.

Analyze this content:

Content: {content}

Determine:
1. Is this mathematics/science/educational content?
2. Contains any truly harmful, illegal, or explicitly inappropriate content?

IMPORTANT: 
- ALL math problems, equations, physics, chemistry questions should be ALLOWED
- Only BLOCK content that is clearly harmful, illegal, hateful, or explicit
- Questions about solving equations, finding values, calculus, algebra, geometry are ALWAYS allowed
- Simple math questions like "2x+7=0 find x" are EDUCATIONAL and should be allowed

Provide JSON response:
{{
    "is_safe": true,
    "is_educational": true,
    "is_mathematical": true,
    "confidence": 0.95,
    "issues": [],
    "recommendation": "allow",
    "category": "mathematics"
}}

Default to ALLOW for any mathematical or educational content."""

        response = self.call_llm(prompt)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    safety = json.loads(json_str)
                    return safety
            except Exception as e:
                self.logger.error(f"Failed to parse LLM safety check: {e}")
        
        return self._basic_check(content)
    
    def _basic_check(self, content: str) -> Dict[str, Any]:
        """Basic safety check when LLM is unavailable"""
        
        # Only block truly harmful content - be very permissive for education
        harmful_keywords = ['porn', 'explicit', 'illegal', 'bomb', 'weapon', 'kill']
        has_issues = any(keyword in content.lower() for keyword in harmful_keywords)
        
        # Math/educational keywords - if found, definitely allow
        math_keywords = ['solve', 'find', 'calculate', 'derivative', 'integral', 'equation', 
                        'value', 'x', 'y', 'formula', 'theorem', 'proof']
        is_math = any(keyword in content.lower() for keyword in math_keywords)
        
        return {
            "is_safe": not has_issues,
            "is_educational": True,
            "is_mathematical": is_math or not has_issues,
            "confidence": 0.95 if is_math else 0.6,
            "issues": ["Potentially harmful content detected"] if has_issues else [],
            "recommendation": "block" if has_issues else "allow",
            "category": "mathematics" if is_math else "other"
        }
