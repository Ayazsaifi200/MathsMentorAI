#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend Testing Script for Math Mentor AI
Tests the complete problem-solving pipeline without UI
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

import logging
from src.agents.parser_agent import ParserAgent
from src.agents.intent_router_agent import IntentRouterAgent
from src.agents.solver_agent import SolverAgent
from src.agents.verifier_agent import VerifierAgent
from src.agents.explainer_agent import ExplainerAgent
from src.rag.knowledge_base import MathKnowledgeRAG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackendTester:
    """Tests the Math Mentor AI backend components"""
    
    def __init__(self):
        """Initialize all agents and RAG system"""
        logger.info("Initializing backend components...")
        
        try:
            self.parser = ParserAgent()
            logger.info("✓ Parser Agent initialized")
        except Exception as e:
            logger.error(f"✗ Parser Agent failed: {e}")
            self.parser = None
        
        try:
            self.router = IntentRouterAgent()
            logger.info("✓ Intent Router Agent initialized")
        except Exception as e:
            logger.error(f"✗ Intent Router Agent failed: {e}")
            self.router = None
        
        try:
            self.solver = SolverAgent()
            logger.info("✓ Solver Agent initialized")
            
            # Check if LLM is available
            if hasattr(self.solver, 'llm_available') and self.solver.llm_available:
                logger.info("  → Google Gemini Pro: AVAILABLE ✓")
            else:
                logger.warning("  → Google Gemini Pro: NOT AVAILABLE ✗")
            
            # Check if SymPy is available
            if hasattr(self.solver, 'sympy_available') and self.solver.sympy_available:
                logger.info("  → SymPy (Symbolic Math): AVAILABLE ✓")
            else:
                logger.warning("  → SymPy: NOT AVAILABLE ✗")
                
        except Exception as e:
            logger.error(f"✗ Solver Agent failed: {e}")
            self.solver = None
        
        try:
            self.verifier = VerifierAgent()
            logger.info("✓ Verifier Agent initialized")
        except Exception as e:
            logger.error(f"✗ Verifier Agent failed: {e}")
            self.verifier = None
        
        try:
            self.explainer = ExplainerAgent()
            logger.info("✓ Explainer Agent initialized")
        except Exception as e:
            logger.error(f"✗ Explainer Agent failed: {e}")
            self.explainer = None
        
        try:
            self.rag = MathKnowledgeRAG()
            stats = self.rag.get_knowledge_statistics()
            logger.info(f"✓ RAG System initialized ({stats['total_documents']} documents)")
        except Exception as e:
            logger.error(f"✗ RAG System failed: {e}")
            self.rag = None
    
    def test_simple_algebra(self):
        """Test 1: Simple Algebraic Equation"""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Simple Algebraic Equation")
        logger.info("="*60)
        
        problem_text = "Solve the equation: 2x + 5 = 15"
        return self._run_full_pipeline(problem_text, "algebra")
    
    def test_quadratic_equation(self):
        """Test 2: Quadratic Equation"""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Quadratic Equation")
        logger.info("="*60)
        
        problem_text = "Solve the quadratic equation: x² - 5x + 6 = 0"
        return self._run_full_pipeline(problem_text, "algebra")
    
    def test_calculus_derivative(self):
        """Test 3: Calculus Derivative"""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Calculus Derivative")
        logger.info("="*60)
        
        problem_text = "Find the derivative of f(x) = x³ + 2x² - 5x + 3"
        return self._run_full_pipeline(problem_text, "calculus")
    
    def test_probability(self):
        """Test 4: Probability Problem"""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: Probability")
        logger.info("="*60)
        
        problem_text = "A coin is tossed 3 times. What is the probability of getting exactly 2 heads?"
        return self._run_full_pipeline(problem_text, "probability")
    
    def test_geometry(self):
        """Test 5: Geometry Problem"""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: Geometry")
        logger.info("="*60)
        
        problem_text = "Find the area of a triangle with base 10 cm and height 8 cm"
        return self._run_full_pipeline(problem_text, "geometry")
    
    def _run_full_pipeline(self, problem_text, expected_topic=None):
        """Run complete problem-solving pipeline"""
        logger.info(f"\nProblem: {problem_text}")
        
        try:
            # Step 1: Parse the problem
            logger.info("\n[STEP 1: PARSING]")
            if not self.parser:
                logger.error("Parser not available")
                return False
            
            parse_input = {"problem_text": problem_text}
            parsed_result = self.parser.process(parse_input)
            
            if not parsed_result.get("success"):
                logger.error(f"Parsing failed: {parsed_result.get('error')}")
                return False
            
            logger.info(f"✓ Problem parsed successfully")
            logger.info(f"  Topic detected: {parsed_result.get('topic', 'unknown')}")
            logger.info(f"  Problem type: {parsed_result.get('problem_type', 'unknown')}")
            
            # Step 2: Route to strategy
            logger.info("\n[STEP 2: ROUTING]")
            if not self.router:
                logger.error("Router not available")
                return False
            
            router_input = {
                "problem_text": problem_text,
                "parsed_problem": parsed_result
            }
            routing_result = self.router.process(router_input)
            
            if not routing_result.get("success"):
                logger.error(f"Routing failed: {routing_result.get('error')}")
                return False
            
            logger.info(f"✓ Strategy determined")
            logger.info(f"  Primary strategy: {routing_result.get('primary_strategy', 'unknown')}")
            logger.info(f"  Complexity: {routing_result.get('complexity_level', 'unknown')}")
            
            # Step 3: Solve the problem
            logger.info("\n[STEP 3: SOLVING]")
            if not self.solver:
                logger.error("Solver not available")
                return False
            
            # Get relevant knowledge
            knowledge = []
            if self.rag:
                topic = parsed_result.get('topic', 'general')
                knowledge = self.rag.get_knowledge_for_problem_type(topic, top_k=3)
                logger.info(f"  Retrieved {len(knowledge)} knowledge documents")
            
            solver_input = {
                "problem_text": problem_text,
                "parsed_problem": parsed_result,
                "solution_strategy": routing_result.get('primary_strategy'),
                "relevant_knowledge": knowledge
            }
            solution_result = self.solver.process(solver_input)
            
            if not solution_result.get("success"):
                logger.error(f"Solving failed: {solution_result.get('error')}")
                return False
            
            logger.info(f"✓ Problem solved")
            logger.info(f"  Solution type: {solution_result.get('solution_type', 'unknown')}")
            logger.info(f"  Confidence: {solution_result.get('confidence', 0):.2%}")
            logger.info(f"  Final answer: {solution_result.get('final_answer', 'N/A')}")
            
            # Step 4: Verify the solution
            logger.info("\n[STEP 4: VERIFICATION]")
            if not self.verifier:
                logger.error("Verifier not available")
                return False
            
            verifier_input = {
                "problem_text": problem_text,
                "solution": {
                    "solution_steps": solution_result.get('solution_steps', ''),
                    "final_answer": solution_result.get('final_answer'),
                    "solution_type": solution_result.get('solution_type', 'unknown')
                }
            }
            verification_result = self.verifier.process(verifier_input)
            
            if not verification_result.get("success"):
                logger.error(f"Verification failed: {verification_result.get('error')}")
                return False
            
            logger.info(f"✓ Solution verified")
            logger.info(f"  Verification passed: {verification_result.get('verification_passed', False)}")
            logger.info(f"  Verification confidence: {verification_result.get('verification_confidence', 0):.2%}")
            logger.info(f"  Needs human review: {verification_result.get('needs_human_review', False)}")
            
            if verification_result.get('errors_found'):
                logger.warning(f"  Errors found: {len(verification_result['errors_found'])}")
            
            # Step 5: Generate explanation
            logger.info("\n[STEP 5: EXPLANATION]")
            if not self.explainer:
                logger.error("Explainer not available")
                return False
            
            explainer_input = {
                "problem_text": problem_text,
                "solution_steps": solution_result.get('solution_steps', ''),
                "final_answer": solution_result.get('final_answer'),
                "topic": parsed_result.get('topic')
            }
            explanation_result = self.explainer.process(explainer_input)
            
            if not explanation_result.get("success"):
                logger.error(f"Explanation failed: {explanation_result.get('error')}")
                return False
            
            logger.info(f"✓ Explanation generated")
            
            # Print solution summary
            logger.info("\n" + "="*60)
            logger.info("SOLUTION SUMMARY")
            logger.info("="*60)
            logger.info(f"\nProblem: {problem_text}")
            logger.info(f"\nAnswer: {solution_result.get('final_answer', 'N/A')}")
            logger.info(f"\nSolution Steps:\n{solution_result.get('solution_steps', 'N/A')[:500]}...")
            logger.info(f"\nVerification: {'PASSED ✓' if verification_result.get('verification_passed') else 'FAILED ✗'}")
            logger.info("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            return False
    
    def run_all_tests(self):
        """Run all test cases"""
        logger.info("\n" + "#"*60)
        logger.info("# MATH MENTOR AI - BACKEND TESTING")
        logger.info("#"*60)
        
        tests = [
            ("Simple Algebra", self.test_simple_algebra),
            ("Quadratic Equation", self.test_quadratic_equation),
            ("Calculus Derivative", self.test_calculus_derivative),
            ("Probability", self.test_probability),
            ("Geometry", self.test_geometry)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                logger.error(f"Test '{test_name}' crashed: {e}")
                results.append((test_name, False))
        
        # Print summary
        logger.info("\n" + "#"*60)
        logger.info("# TEST RESULTS SUMMARY")
        logger.info("#"*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"{test_name:.<40} {status}")
        
        logger.info(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        logger.info("#"*60)
        
        return passed == total


if __name__ == "__main__":
    logger.info("Starting Math Mentor AI Backend Tests...")
    
    tester = BackendTester()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        logger.info("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        sys.exit(0)
    else:
        logger.error("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
        sys.exit(1)
