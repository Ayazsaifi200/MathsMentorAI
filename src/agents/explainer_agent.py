# -*- coding: utf-8 -*-
"""
Explainer Agent for Math Mentor AI
Uses LLM to generate educational explanations
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class ExplainerAgent(BaseAgent):
    """AI-powered agent for generating educational explanations"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define explainer agent capabilities"""
        return AgentCapability(
            name="ExplainerAgent",
            description="Use AI to generate clear educational explanations",
            input_types=["solution", "verification_result"],
            output_types=["explanation"],
            dependencies=["SolverAgent", "VerifierAgent"],
            confidence_threshold=0.7
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to explain the solution educationally
        
        Args:
            input_data: Contains problem, solution, and verification
            
        Returns:
            Educational explanation with concepts and insights
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        problem_text = input_data.get("problem_text", "")
        solution = input_data.get("solution", {})
        
        # Use LLM for educational explanations
        if self.llm_available:
            explanation = self._explain_with_ai(problem_text, solution)
        else:
            explanation = self._basic_explanation(solution)
        
        return self.create_success_response(explanation)
    
    def _explain_with_ai(self, problem_text: str, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to generate educational explanation"""
        
        final_answer = solution.get("final_answer", "")
        steps = solution.get("solution_steps", [])
        
        prompt = f"""You are an expert mathematics educator explaining a solution to a JEE student.

Problem: {problem_text}

Solution: {final_answer}

Steps: {json.dumps(steps, indent=2)}

Provide an educational explanation in JSON format:
{{
    "conceptual_overview": "High-level explanation of the approach and why it works",
    "key_insights": [
        "Important insight 1",
        "Important insight 2"
    ],
    "step_by_step_explanation": [
        {{
            "step": "description of step",
            "why": "why this step is necessary",
            "concept": "underlying mathematical concept"
        }}
    ],
    "common_mistakes": [
        "Common mistake students make with this type of problem"
    ],
    "related_concepts": [
        "Related concept 1",
        "Related concept 2"
    ],
    "practice_tips": "How to practice and master this type of problem",
    "real_world_application": "How this concept applies in real world (if applicable)"
}}

Make it educational and insightful for JEE preparation."""

        response = self.call_llm(prompt)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    explanation = json.loads(json_str)
                    return explanation
            except Exception as e:
                self.logger.error(f"Failed to parse LLM explanation: {e}")
        
        return self._basic_explanation(solution)
    
    def _basic_explanation(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Basic explanation when LLM is unavailable"""
        steps = solution.get("solution_steps", [])
        
        return {
            "conceptual_overview": "Solution follows standard mathematical problem-solving approach",
            "key_insights": ["Follow systematic steps", "Verify your answer"],
            "step_by_step_explanation": [
                {
                    "step": step.get("description", ""),
                    "why": step.get("reasoning", ""),
                    "concept": "mathematical reasoning"
                }
                for step in steps
            ],
            "common_mistakes": [],
            "related_concepts": [],
            "practice_tips": "Practice similar problems to build understanding",
            "real_world_application": None
        }
