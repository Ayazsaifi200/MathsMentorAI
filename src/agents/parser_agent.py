# -*- coding: utf-8 -*-
"""
Parser Agent for Math Mentor AI
Uses LLM to intelligently parse and understand any mathematical problem
"""

import json
import logging
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class ParserAgent(BaseAgent):
    """AI-powered agent for parsing mathematical problems"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define parser agent capabilities"""
        return AgentCapability(
            name="ParserAgent",
            description="Use AI to parse and understand any mathematical problem",
            input_types=["text", "image", "audio"],
            output_types=["parsed_problem"],
            dependencies=[],
            confidence_threshold=0.6
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to parse and understand the mathematical problem
        
        Args:
            input_data: Contains 'problem_text'
            
        Returns:
            AI-parsed problem with deep understanding
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        problem_text = input_data.get("problem_text", "")
        if not problem_text:
            return self.create_error_response("No problem text provided")
        
        # Use LLM to deeply understand the problem
        if self.llm_available:
            parsed = self._parse_with_ai(problem_text)
        else:
            # Fallback to basic parsing
            parsed = self._basic_parse(problem_text)
        
        return self.create_success_response(parsed)
    
    def _parse_with_ai(self, problem_text: str) -> Dict[str, Any]:
        """Use AI to parse and understand the problem"""
        
        prompt = f"""You are an expert mathematics educator analyzing JEE-level problems.

Analyze this mathematical problem and extract key information:

Problem: {problem_text}

Provide a structured analysis in JSON format with these fields:
{{
    "problem_text": "the original problem",
    "topic": "main mathematical topic (algebra/calculus/geometry/trigonometry/probability/statistics/linear_algebra/coordinate_geometry/vectors/complex_numbers/etc)",
    "subtopic": "specific subtopic or concept",
    "difficulty": "JEE Main/JEE Advanced/Olympiad",
    "problem_type": "what type of problem (equation/proof/calculation/optimization/word_problem/etc)",
    "variables": ["list of variables like x, y, n, etc."],
    "constraints": ["list of constraints like x > 0, n is integer, etc."],
    "key_concepts": ["list", "of", "key", "concepts"],
    "given_information": ["list of given values and conditions"],
    "what_to_find": "what the problem is asking to find or prove",
    "approach_hints": ["possible", "approaches", "to", "solve"],
    "needs_clarification": false
}}

Set needs_clarification to true ONLY if the problem text is genuinely ambiguous, incomplete, or missing critical information needed to solve it (e.g. undefined variables, missing equation, contradictory conditions). Normal well-formed problems should always be false.

Think carefully about the mathematical structure and provide detailed analysis."""

        response = self.call_llm(prompt)
        
        if response:
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    parsed = json.loads(json_str)
                    # Ensure required fields exist with defaults
                    parsed.setdefault('variables', [])
                    parsed.setdefault('constraints', [])
                    parsed.setdefault('needs_clarification', False)
                    return parsed
            except Exception as e:
                self.logger.error(f"Failed to parse LLM response: {e}")
        
        # Fallback
        return self._basic_parse(problem_text)
    
    def _basic_parse(self, problem_text: str) -> Dict[str, Any]:
        """Basic parsing fallback when LLM is unavailable"""
        import re
        # Extract variables: single letters that appear as likely math vars
        var_pattern = re.findall(r'\b([a-zA-Z])\b', problem_text)
        variables = list(set(v for v in var_pattern if v.lower() not in ('a', 'i', 'is', 'or', 'if', 'in', 'of', 'to')))
        # Extract constraints like x > 0, n >= 1
        constraints = re.findall(r'[a-zA-Z]\s*[><=!]+\s*\d+', problem_text)
        # Ambiguity: if very short or mostly non-math
        needs_clarification = len(problem_text.strip()) < 10
        return {
            "problem_text": problem_text,
            "topic": "general",
            "subtopic": "unknown",
            "difficulty": "JEE",
            "problem_type": "general",
            "variables": variables,
            "constraints": constraints,
            "key_concepts": [],
            "given_information": [],
            "what_to_find": "solution",
            "approach_hints": [],
            "needs_clarification": needs_clarification
        }
