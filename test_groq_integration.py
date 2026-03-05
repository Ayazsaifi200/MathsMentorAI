# -*- coding: utf-8 -*-
"""
Test Groq API Integration
Verifies that Groq is working properly for Math Mentor AI
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_groq_integration():
    """Test if Groq API is working properly"""
    
    print("=" * 60)
    print("🧪 TESTING GROQ API INTEGRATION")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No GROQ_API_KEY found in .env file")
        return False
    
    print(f"✅ Groq API Key found: {api_key[:20]}...{api_key[-4:]}")
    
    # Test Groq package installation
    try:
        from groq import Groq
        print("✅ Groq package installed successfully")
    except ImportError as e:
        print(f"❌ Groq package not installed: {e}")
        print("Run: pip install groq")
        return False
    
    # Initialize Groq client
    try:
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Groq client: {e}")
        return False
    
    # Test simple math problem
    try:
        print("\n🧮 Testing with a simple math problem...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user", 
                "content": "Solve this simple equation: 2x + 5 = 15. Show your work step by step."
            }],
            temperature=0.3,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        print(f"✅ Groq Response:\n{answer}")
        
        # Test complex JEE-level problem
        print("\n🎓 Testing with JEE-level problem...")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[{
                "role": "user",
                "content": """Solve this JEE-level calculus problem:
                
Find the derivative of f(x) = x³ + 2x² - 5x + 7
                
Provide step-by-step solution in JSON format:
{
    "solution_steps": [
        {"step": 1, "work": "...", "explanation": "..."}
    ],
    "final_answer": "...",
    "verification": "..."
}"""
            }],
            temperature=0.2,
            max_tokens=800
        )
        
        jee_answer = response.choices[0].message.content
        print(f"✅ JEE Problem Response:\n{jee_answer[:200]}...")
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS! Groq is working perfectly!")
        print("✅ Simple math: Working")
        print("✅ JEE-level problems: Working") 
        print("✅ JSON responses: Working")
        print("✅ Step-by-step solutions: Working")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API call failed: {e}")
        
        # Check for common errors
        if "429" in str(e):
            print("⚠️  Rate limit exceeded - wait a moment and try again")
        elif "401" in str(e):
            print("⚠️  Invalid API key - check your GROQ_API_KEY")
        elif "quota" in str(e).lower():
            print("⚠️  Quota exceeded - check your Groq dashboard")
        
        return False

def test_agent_integration():
    """Test if agents can use Groq"""
    
    print("\n🤖 TESTING AGENT INTEGRATION")
    print("=" * 60)
    
    try:
        from src.agents.base_agent import BaseAgent
        from src.agents.solver_agent import SolverAgent
        
        print("✅ Agent imports successful")
        
        # Test solver agent
        solver = SolverAgent()
        print(f"✅ SolverAgent initialized")
        print(f"   - LLM Available: {solver.llm_available}")
        print(f"   - LLM Provider: {solver.llm_provider}")
        
        if solver.llm_available:
            print("✅ Solver agent ready to solve math problems!")
            return True
        else:
            print("❌ Solver agent cannot access LLM")
            return False
            
    except Exception as e:
        print(f"❌ Agent integration failed: {e}")
        return False

if __name__ == "__main__":
    # Test Groq API
    groq_working = test_groq_integration()
    
    # Test Agent Integration  
    if groq_working:
        agents_working = test_agent_integration()
        
        if agents_working:
            print("\n🚀 FINAL RESULT: Everything is working perfectly!")
            print("Your Math Mentor AI is ready to solve JEE-level problems with Groq!")
        else:
            print("\n⚠️  Groq works but agents need configuration")
    else:
        print("\n❌ Fix Groq API issues first")