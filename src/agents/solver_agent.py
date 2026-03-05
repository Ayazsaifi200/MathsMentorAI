# -*- coding: utf-8 -*-
"""
Solver Agent for Math Mentor AI
Uses LLM to solve ANY mathematical problem through AI reasoning
"""

import json
import logging
import re
from typing import Dict, Any
from .base_agent import BaseAgent, AgentCapability

logger = logging.getLogger(__name__)


class SolverAgent(BaseAgent):
    """AI-powered agent for solving mathematical problems"""
    
    def _define_capabilities(self) -> AgentCapability:
        """Define solver agent capabilities"""
        return AgentCapability(
            name="SolverAgent",
            description="Use AI to solve ANY mathematical problem through reasoning",
            input_types=["parsed_problem", "strategy"],
            output_types=["solution"],
            dependencies=["ParserAgent", "IntentRouterAgent"],
            confidence_threshold=0.75
        )
    
    def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Use LLM to solve the mathematical problem
        
        Args:
            input_data: Contains problem information and strategy
            
        Returns:
            Complete solution with steps and answer
        """
        if not self.validate_input(input_data):
            return self.create_error_response("Invalid input format")
        
        problem_text = input_data.get("problem_text", "")
        if not problem_text:
            return self.create_error_response("No problem text provided")
        
        # Use LLM for AI-powered solving
        if self.llm_available:
            solution = self._solve_with_ai(input_data)
        else:
            solution = self._fallback_message()
        
        return self.create_success_response(solution)
    
    def _solve_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to solve the problem through reasoning"""
        
        problem_text = data.get("problem_text", "")
        topic = data.get("topic", "general")
        strategy = data.get("strategy", {})
        memory_context = data.get("memory_context", "")
        
        memory_section = ""
        if memory_context:
            memory_section = f"\n\nContext from previously solved problems and learned strategies:\n{memory_context}\nUse this context to inform your approach if relevant, but solve the current problem independently.\n"
        
        prompt = f"""You are an expert mathematics tutor solving JEE-level problems.

Problem: {problem_text}

Topic: {topic}{memory_section}

Solve this problem step-by-step and provide the answer in proper LaTeX mathematical notation.

Your response MUST be valid JSON with this EXACT format:
{{
    "solution_steps": [
        {{
            "step_number": 1,
            "description": "Clear explanation of what we're doing",
            "mathematical_work": "The actual math work with LaTeX notation",
            "reasoning": "Why we're doing this step"
        }}
    ],
    "final_answer": "x = \\\\frac{{1}}{{5}}",
    "answer_format": "latex",
    "verification": "Quick check that the answer is correct"
}}

CRITICAL LaTeX Rules for JSON:
1. Use DOUBLE backslashes in JSON: \\\\frac{{a}}{{b}} (becomes \\frac{{a}}{{b}} when parsed)
2. Fractions: x = \\\\frac{{numerator}}{{denominator}}
3. Exponents: x^{{2}} or x^{{n}}
4. Square roots: \\\\sqrt{{x}} or \\\\sqrt[n]{{x}}
5. Trigonometric: \\\\sin, \\\\cos, \\\\tan, etc.
6. Greek letters: \\\\alpha, \\\\beta, \\\\theta, \\\\pi
7. Always use double curly braces {{{{ }}}} in JSON to represent single braces

Example final_answer formats:
- Simple: "x = 5"
- Fraction: "x = \\\\frac{{1}}{{2}}"
- Quadratic: "x = \\\\frac{{-b \\\\pm \\\\sqrt{{b^2 - 4ac}}}}{{2a}}"
- Trig: "\\\\theta = \\\\frac{{\\\\pi}}{{4}}"

Return ONLY the JSON, no additional text."""

        try:
            response = self.call_llm(prompt, max_retries=3)
            
            if not response:
                self.logger.error("LLM returned empty response")
                return self._fallback_message()
            
            self.logger.info(f"LLM Response (first 500 chars): {response[:500]}")
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    solution = json.loads(json_str)
                    self.logger.info(f"Parsed solution successfully")
                    # Log the final_answer to check encoding
                    if 'final_answer' in solution:
                        self.logger.info(f"Final answer from LLM: {repr(solution['final_answer'])}")
                    return solution
                else:
                    self.logger.warning("No JSON found in response")
                    return self._extract_solution_from_text(response)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing failed: {e}")
                return self._extract_solution_from_text(response)
        except Exception as e:
            self.logger.error(f"Error in _solve_with_ai: {e}", exc_info=True)
            return self._fallback_message()
    
    def _extract_solution_from_text(self, text: str) -> Dict[str, Any]:
        """Extract solution from unstructured LLM response"""
        
        # Try to find the final answer
        answer_patterns = [
            r"final answer:?\s*(.+?)(?:\n|$)",
            r"answer:?\s*(.+?)(?:\n|$)",
            r"therefore,?\s*(.+?)(?:\n|$)",
            r"solution:?\s*(.+?)(?:\n|$)"
        ]
        
        answer = None
        for pattern in answer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                answer = match.group(1).strip()
                break
        
        return {
            "solution_steps": [{
                "step_number": 1,
                "description": "AI-generated solution",
                "mathematical_work": text,
                "reasoning": "LLM reasoning"
            }],
            "final_answer": answer or "Unable to extract answer",
            "answer_format": "text",
            "verification": "See solution steps"
        }
    
    def _fallback_message(self) -> Dict[str, Any]:
        """Fallback when LLM is unavailable"""
        return {
            "solution_steps": [{
                "step_number": 1,
                "description": "WARNING: Groq API Daily Quota Exceeded",
                "mathematical_work": "Your Groq API has reached its daily token limit (100,000 tokens/day for free tier). The quota will reset in a few hours. Solutions: (1) Wait for quota reset, (2) Upgrade at https://console.groq.com/settings/billing, or (3) Use a different API key.",
                "reasoning": "Rate limit: 429 error from Groq AI API"
            }],
            "final_answer": "Groq API quota exceeded - Please wait for reset or upgrade",
            "answer_format": "error",
            "verification": "Check your quota at https://console.groq.com"
        }
