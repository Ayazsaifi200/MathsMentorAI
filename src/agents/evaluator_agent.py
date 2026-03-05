# -*- coding: utf-8 -*-
"""
Evaluator Agent for Math Mentor AI
Uses LLM to evaluate overall solution quality and provide feedback
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """AI-powered agent for evaluating solution quality"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define evaluator agent capabilities"""
        return AgentCapability(
            name="EvaluatorAgent",
            description="Use AI to evaluate overall solution quality and provide feedback",
            input_types=["solution", "explanation", "verification_result"],
            output_types=["evaluation"],
            dependencies=["SolverAgent", "VerifierAgent", "ExplainerAgent"],
            confidence_threshold=0.75
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to evaluate the complete solution
        
        Args:
            input_data: Contains problem, solution, verification, and explanation
            
        Returns:
            Overall quality evaluation and feedback
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        # Use LLM for comprehensive evaluation
        if self.llm_available:
            evaluation = self._evaluate_with_ai(input_data)
        else:
            evaluation = self._basic_evaluation(input_data)
        
        return self.create_success_response(evaluation)
    
    def _evaluate_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to evaluate solution quality"""
        
        problem_text = data.get("problem_text", "")
        solution = data.get("solution", {})
        verification = data.get("verification", {})
        explanation = data.get("explanation", {})
        
        prompt = f"""You are an expert mathematics educator evaluating a complete solution.

Problem: {problem_text}

Solution: {json.dumps(solution, indent=2)}

Verification: {json.dumps(verification, indent=2)}

Explanation: {json.dumps(explanation, indent=2)}

Evaluate the overall quality and provide feedback in JSON format:
{{
    "overall_quality": "excellent/good/fair/poor",
    "quality_score": 0.0-1.0,
    "strengths": [
        "What was done well"
    ],
    "weaknesses": [
        "What could be improved"
    ],
    "correctness_assessment": "correct/incorrect/partially_correct",
    "clarity_score": 0.0-1.0,
    "educational_value": 0.0-1.0,
    "feedback_for_student": "Constructive feedback to help the student learn",
    "improvement_suggestions": [
        "Specific suggestions for improvement"
    ],
    "next_steps": "What the student should study or practice next"
}}

Provide constructive, educational feedback."""

        response = self.call_llm(prompt)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    evaluation = json.loads(json_str)
                    return evaluation
            except Exception as e:
                self.logger.error(f"Failed to parse LLM evaluation: {e}")
        
        return self._basic_evaluation(data)
    
    def _basic_evaluation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic evaluation when LLM is unavailable"""
        
        solution = data.get("solution", {})
        verification = data.get("verification", {})
        
        has_answer = bool(solution.get("final_answer"))
        is_verified = verification.get("is_correct", False)
        
        if is_verified:
            quality = "good"
            score = 0.8
        elif has_answer:
            quality = "fair"
            score = 0.6
        else:
            quality = "poor"
            score = 0.3
        
        return {
            "overall_quality": quality,
            "quality_score": score,
            "strengths": ["Solution provided"] if has_answer else [],
            "weaknesses": [] if is_verified else ["Verification needed"],
            "correctness_assessment": "correct" if is_verified else "unknown",
            "clarity_score": 0.7,
            "educational_value": 0.7,
            "feedback_for_student": "Continue practicing to improve",
            "improvement_suggestions": [],
            "next_steps": "Practice similar problems"
        }
