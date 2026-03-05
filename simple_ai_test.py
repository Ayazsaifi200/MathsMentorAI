# -*- coding: utf-8 -*-
"""
Simple Math Mentor AI Test
Quick test to verify core AI functionality is working
"""

from src.agents import SolverAgent
import logging

def test_ai_solving():
    """Test AI solving with Groq"""
    print("🧮 MATH MENTOR AI - QUICK TEST")
    print("="*50)
    
    # Initialize solver
    solver = SolverAgent()
    print(f"✅ Solver initialized with: {solver.llm_provider.upper()}")
    
    if not solver.llm_available:
        print("❌ LLM not available")
        return False
    
    # Test problems
    problems = [
        "Solve: 2x + 5 = 15",
        "Find derivative of x² + 3x",
        "Area of triangle with base 8cm, height 6cm"
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\nTest {i}: {problem}")
        
        # Create input for solver
        input_data = {
            "problem_text": problem,
            "topic": "math"
        }
        
        # Solve with AI
        result = solver.process(input_data)
        
        if result.get("success"):
            answer = result.get("final_answer", "No answer")
            print(f"✅ Answer: {answer}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*50)
    print("🎉 AI TEST COMPLETE!")
    return True

if __name__ == "__main__":
    test_ai_solving()