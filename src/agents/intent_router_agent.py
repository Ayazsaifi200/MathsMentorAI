# -*- coding: utf-8 -*-
"""
Intent Router Agent for Math Mentor AI
Uses LLM to intelligently determine the best solution strategy
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class IntentRouterAgent(BaseAgent):
    """AI-powered agent for routing problems to the best solution strategy"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define router agent capabilities"""
        return AgentCapability(
            name="IntentRouterAgent",
            description="Use AI to determine the best strategy for solving a problem",
            input_types=["parsed_problem"],
            output_types=["strategy"],
            dependencies=["ParserAgent"],
            confidence_threshold=0.7
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to determine the best solution strategy
        
        Args:
            input_data: Contains parsed problem information
            
        Returns:
            Recommended strategy and approach
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        # Use LLM for intelligent routing
        if self.llm_available:
            strategy = self._route_with_ai(input_data)
        else:
            strategy = self._default_strategy(input_data)
        
        return self.create_success_response(strategy)
    
    def _route_with_ai(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to determine the best solution strategy"""
        
        problem_text = parsed_data.get("problem_text", "")
        topic = parsed_data.get("topic", "")
        
        prompt = f"""You are an expert mathematics educator planning how to solve a JEE problem.

Problem: {problem_text}
Topic: {topic}

Determine the best solution strategy. Provide a JSON response:
{{
    "strategy": "step-by-step/direct-computation/proof/geometric-construction/algebraic-manipulation/calculus-application/etc",
    "approach": "detailed approach description",
    "key_steps": ["step 1", "step 2", "step 3"],
    "tools_needed": ["algebra", "calculus", "geometry", "trigonometry", "etc"],
    "estimated_complexity": "simple/moderate/complex",
    "common_pitfalls": ["potential mistakes to avoid"]
}}

Think carefully about the most effective approach."""

        response = self.call_llm(prompt)
        
        if response:
            try:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    # Fix common JSON escape issues
                    json_str = json_str.replace('\\', '\\\\')  # Fix backslashes
                    json_str = json_str.replace('\\"', '"')    # Fix quotes
                    strategy = json.loads(json_str)
                    return strategy
            except Exception as e:
                self.logger.error(f"Failed to parse LLM response: {e}")
                # Try to extract strategy from text if JSON fails
                return self._extract_strategy_from_text(response)
        
        return self._default_strategy(parsed_data)
    
    def _extract_strategy_from_text(self, text: str) -> Dict[str, Any]:
        """Extract strategy from unstructured text when JSON parsing fails"""
        return {
            "strategy": "step-by-step",
            "approach": "AI-generated strategy",
            "key_steps": ["Parse problem", "Apply methods", "Solve systematically"],
            "tools_needed": ["algebra"],
            "estimated_complexity": "moderate",
            "common_pitfalls": []
        }
    
    def _default_strategy(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Default strategy when LLM is unavailable"""
        return {
            "strategy": "step-by-step",
            "approach": "Solve using systematic mathematical reasoning",
            "key_steps": ["Understand the problem", "Apply mathematical methods", "Verify solution"],
            "tools_needed": ["algebra"],
            "estimated_complexity": "moderate",
            "common_pitfalls": []
        }
