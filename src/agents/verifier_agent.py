# -*- coding: utf-8 -*-
"""
Verifier Agent for Math Mentor AI
Uses LLM to verify mathematical solutions
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class VerifierAgent(BaseAgent):
    """AI-powered agent for verifying mathematical solutions"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define verifier agent capabilities"""
        return AgentCapability(
            name="VerifierAgent",
            description="Use AI to verify solution correctness",
            input_types=["solution"],
            output_types=["verification_result"],
            dependencies=["SolverAgent"],
            confidence_threshold=0.8
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to verify the solution
        
        Args:
            input_data: Contains problem and solution
            
        Returns:
            Verification results with confidence
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        problem_text = input_data.get("problem_text", "")
        solution = input_data.get("solution", {})
        
        if not problem_text or not solution:
            return self.create_error_response("Missing problem or solution")
        
        # Use LLM for verification
        if self.llm_available:
            verification = self._verify_with_ai(problem_text, solution)
        else:
            verification = self._basic_verification(solution)
        
        return self.create_success_response(verification)
    
    def _verify_with_ai(self, problem_text: str, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to verify the solution"""
        
        final_answer = solution.get("final_answer", "")
        steps = solution.get("solution_steps", [])
        
        prompt = f"""You are an expert mathematics educator verifying a solution.

Original Problem: {problem_text}

Proposed Solution:
Final Answer: {final_answer}

Solution Steps:
{json.dumps(steps, indent=2)}

Verify this solution carefully. Provide a JSON response:
{{
    "is_correct": true/false,
    "confidence": 0.0-1.0,
    "issues_found": ["list of any errors or issues"],
    "verification_method": "how you verified (substitution/logical_check/calculation_check/etc)",
    "alternative_answer": "if incorrect, what the correct answer should be (or null)",
    "reasoning": "explain your verification process"
}}

Check:
- Mathematical accuracy
- Logical consistency
- Calculation correctness
- Final answer validity"""

        response = self.call_llm(prompt)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    verification = json.loads(json_str)
                    return verification
            except Exception as e:
                self.logger.error(f"Failed to parse LLM verification: {e}")
        
        return self._basic_verification(solution)
    
    def _basic_verification(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Basic verification when LLM is unavailable"""
        has_answer = bool(solution.get("final_answer"))
        
        return {
            "is_correct": has_answer,
            "confidence": 0.5,
            "issues_found": [] if has_answer else ["No answer provided"],
            "verification_method": "basic_check",
            "alternative_answer": None,
            "reasoning": "Basic verification - LLM unavailable"
        }
