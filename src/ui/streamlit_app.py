# -*- coding: utf-8 -*-
"""
Math Mentor AI - Streamlit Application
Production-ready UI for the Multi-Agent RAG System
"""

import streamlit as st
import time
import uuid
import json
import io
import base64
from datetime import datetime
from pathlib import Path
import logging
import tempfile
import os as _os
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import application modules with fallback handling
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import with error handling
try:
    from src.input_processing.input_coordinator import InputCoordinator, InputType
    from src.agents.parser_agent import ParserAgent
    from src.agents.intent_router_agent import IntentRouterAgent
    from src.agents.solver_agent import SolverAgent
    from src.agents.verifier_agent import VerifierAgent
    from src.agents.explainer_agent import ExplainerAgent
    from src.agents.guardrail_agent import GuardrailAgent
    from src.agents.evaluator_agent import EvaluatorAgent
    from src.rag.knowledge_base import MathKnowledgeRAG
    from src.storage.memory_system import MathMentorMemorySystem, InteractionRecord, FeedbackRecord, LearningPattern
    from src.tools.mcp_integration import get_mcp_registry, initialize_mcp
    from src.tools.web_search import WebSearchTool
    from src import config
    MODULES_LOADED = True
except ImportError as e:
    logger.warning(f"Could not import all modules: {e}")
    MODULES_LOADED = False
    
    # Define fallback classes for demo mode
    class MockAgent:
        def __init__(self):
            self.llm_available = True
            self.llm_provider = 'groq'
        def process(self, data):
            return {'success': True, 'result': 'Mock result for demo'}
    
    class MockInputCoordinator:
        def process_input(self, data, input_type):
            return {'processing_successful': True, 'extracted_text': str(data)[:200] if data else ''}
    
    class MockRAG:
        def get_knowledge_for_problem_type(self, topic, top_k=3):
            return [{'content': f'Mock knowledge for {topic}', 'relevance_score': 0.9}]
        def retrieve_relevant_knowledge(self, query, top_k=3):
            return [{'content': f'Mock knowledge for {query}', 'relevance_score': 0.9}]
        def get_knowledge_statistics(self):
            return {'total_documents': 8, 'storage_type': 'ChromaDB'}
    
    class MockMemory:
        def store_interaction(self, interaction):
            return True
        def store_feedback(self, feedback):
            return True
    
    class MockRecord:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    # Assign mock classes
    InputCoordinator = MockInputCoordinator
    ParserAgent = MockAgent
    IntentRouterAgent = MockAgent 
    SolverAgent = MockAgent
    VerifierAgent = MockAgent
    ExplainerAgent = MockAgent
    GuardrailAgent = MockAgent
    EvaluatorAgent = MockAgent
    MathKnowledgeRAG = MockRAG
    MathMentorMemorySystem = MockMemory
    InteractionRecord = MockRecord
    FeedbackRecord = MockRecord
    
    class InputType:
        TEXT = 'text'
        IMAGE = 'image'
        AUDIO = 'audio'

# Import audio recorder component for browser-based microphone recording
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False
    logger.warning("audio-recorder-streamlit not available. Install: pip install audio-recorder-streamlit")

# Load custom CSS
def load_css():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
def initialize_systems():
    """Initialize all backend systems"""
    try:
        if not MODULES_LOADED:
            st.warning("⚠️ Running in demo mode - some modules could not be loaded")
        
        # Initialize input coordinator
        input_coordinator = InputCoordinator()
        
        # Initialize agents
        agents = {
            'parser': ParserAgent(),
            'router': IntentRouterAgent(), 
            'solver': SolverAgent(),
            'verifier': VerifierAgent(),
            'explainer': ExplainerAgent(),
            'guardrail': GuardrailAgent(),
            'evaluator': EvaluatorAgent()
        }
        
        # Initialize RAG system
        rag_system = MathKnowledgeRAG()
        
        # Initialize memory system
        memory_system = MathMentorMemorySystem()
        
        # Initialize MCP registry and register web search tool
        mcp_registry = initialize_mcp()
        web_search = WebSearchTool()
        from src.tools.mcp_integration import MCPTool, MCPToolType
        mcp_registry.register_tool(MCPTool(
            name="web_search",
            description="Search the web for mathematical references and solutions",
            tool_type=MCPToolType.SEARCH,
            execute_fn=lambda query: web_search.search(query, search_type="math"),
            parameters={"query": {"type": "string", "required": True}}
        ))
        
        return {
            'input_coordinator': input_coordinator,
            'agents': agents,
            'rag_system': rag_system,
            'memory_system': memory_system,
            'mcp_registry': mcp_registry,
            'modules_loaded': MODULES_LOADED
        }
    except Exception as e:
        logger.error(f"System initialization error: {str(e)}")
        st.error(f"Failed to initialize systems: {str(e)}")
        return None

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'current_interaction' not in st.session_state:
        st.session_state.current_interaction = None
    
    if 'agent_traces' not in st.session_state:
        st.session_state.agent_traces = []
    
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    
    if 'hitl_reviews' not in st.session_state:
        st.session_state.hitl_reviews = []

# UI Components
def render_header():
    """Render professional header"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 2.5rem; font-weight: 700; color: #fafafa; margin-bottom: 0.5rem;">🧮 Math Mentor AI</h1>
        <p style="font-size: 1.1rem; color: #9ca3af;">Solve any JEE-level math problem with AI</p>
    </div>
    """, unsafe_allow_html=True)

def render_math_symbols():
    """Render complete math symbol toolbar with all symbols"""
    st.markdown("#### 🔤 Quick Insert Math Symbols:")
    
    # Add inline CSS for button boxes - target Streamlit's actual button classes
    st.markdown("""
    <style>
    /* Target all buttons */
    div[data-testid="column"] button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"],
    .stButton button {
        background: transparent !important;
        border: 1px solid #404148 !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.6rem !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #fafafa !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Row 1: Basic operations
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        if st.button("×", key="sym_times", use_container_width=True, help="Multiply"):
            st.session_state.insert_symbol = "×"
    with col2:
        if st.button("÷", key="sym_divide", use_container_width=True, help="Divide"):
            st.session_state.insert_symbol = "÷"
    with col3:
        if st.button("±", key="sym_plusminus", use_container_width=True, help="Plus-minus"):
            st.session_state.insert_symbol = "±"
    with col4:
        if st.button("≠", key="sym_notequal", use_container_width=True, help="Not equal"):
            st.session_state.insert_symbol = "≠"
    with col5:
        if st.button("≤", key="sym_lessequal", use_container_width=True, help="Less or equal"):
            st.session_state.insert_symbol = "≤"
    with col6:
        if st.button("≥", key="sym_greaterequal", use_container_width=True, help="Greater or equal"):
            st.session_state.insert_symbol = "≥"
    with col7:
        if st.button("≈", key="sym_approx", use_container_width=True, help="Approximately"):
            st.session_state.insert_symbol = "≈"
    with col8:
        if st.button("∞", key="sym_infinity", use_container_width=True, help="Infinity"):
            st.session_state.insert_symbol = "∞"
    
    # Row 2: Powers and roots
    col9, col10, col11, col12, col13, col14, col15, col16 = st.columns(8)
    with col9:
        if st.button("²", key="sym_squared", use_container_width=True, help="Squared"):
            st.session_state.insert_symbol = "²"
    with col10:
        if st.button("³", key="sym_cubed", use_container_width=True, help="Cubed"):
            st.session_state.insert_symbol = "³"
    with col11:
        if st.button("ⁿ", key="sym_powern", use_container_width=True, help="Power n"):
            st.session_state.insert_symbol = "ⁿ"
    with col12:
        if st.button("√", key="sym_sqrt", use_container_width=True, help="Square root"):
            st.session_state.insert_symbol = "√"
    with col13:
        if st.button("∛", key="sym_cbrt", use_container_width=True, help="Cube root"):
            st.session_state.insert_symbol = "∛"
    with col14:
        if st.button("∜", key="sym_fourthrt", use_container_width=True, help="Fourth root"):
            st.session_state.insert_symbol = "∜"
    with col15:
        if st.button("¹⁄₂", key="sym_half", use_container_width=True, help="One half"):
            st.session_state.insert_symbol = "¹⁄₂"
    with col16:
        if st.button("ⁿ⁄ₘ", key="sym_frac", use_container_width=True, help="Fraction"):
            st.session_state.insert_symbol = "ⁿ⁄ₘ"
    
    # Row 3: Greek letters
    col17, col18, col19, col20, col21, col22, col23, col24 = st.columns(8)
    with col17:
        if st.button("π", key="sym_pi", use_container_width=True, help="Pi"):
            st.session_state.insert_symbol = "π"
    with col18:
        if st.button("θ", key="sym_theta", use_container_width=True, help="Theta"):
            st.session_state.insert_symbol = "θ"
    with col19:
        if st.button("α", key="sym_alpha", use_container_width=True, help="Alpha"):
            st.session_state.insert_symbol = "α"
    with col20:
        if st.button("β", key="sym_beta", use_container_width=True, help="Beta"):
            st.session_state.insert_symbol = "β"
    with col21:
        if st.button("γ", key="sym_gamma", use_container_width=True, help="Gamma"):
            st.session_state.insert_symbol = "γ"
    with col22:
        if st.button("Δ", key="sym_delta", use_container_width=True, help="Delta"):
            st.session_state.insert_symbol = "Δ"
    with col23:
        if st.button("λ", key="sym_lambda", use_container_width=True, help="Lambda"):
            st.session_state.insert_symbol = "λ"
    with col24:
        if st.button("Σ", key="sym_sigma", use_container_width=True, help="Sigma"):
            st.session_state.insert_symbol = "Σ"
    
    # Row 4: Calculus and trigonometry
    col25, col26, col27, col28, col29, col30, col31, col32 = st.columns(8)
    with col25:
        if st.button("∫", key="sym_integral", use_container_width=True, help="Integral"):
            st.session_state.insert_symbol = "∫"
    with col26:
        if st.button("∬", key="sym_double_int", use_container_width=True, help="Double integral"):
            st.session_state.insert_symbol = "∬"
    with col27:
        if st.button("∂", key="sym_partial", use_container_width=True, help="Partial derivative"):
            st.session_state.insert_symbol = "∂"
    with col28:
        if st.button("∇", key="sym_nabla", use_container_width=True, help="Nabla"):
            st.session_state.insert_symbol = "∇"
    with col29:
        if st.button("lim", key="sym_limit", use_container_width=True, help="Limit"):
            st.session_state.insert_symbol = "lim"
    with col30:
        if st.button("sin", key="sym_sin", use_container_width=True, help="Sine"):
            st.session_state.insert_symbol = "sin"
    with col31:
        if st.button("cos", key="sym_cos", use_container_width=True, help="Cosine"):
            st.session_state.insert_symbol = "cos"
    with col32:
        if st.button("tan", key="sym_tan", use_container_width=True, help="Tangent"):
            st.session_state.insert_symbol = "tan"


def process_text_input(text: str, systems: Dict) -> Dict[str, Any]:
    """Process text input through the agent pipeline"""
    try:
        if not systems.get('modules_loaded', True):
            # Demo mode - simulate processing
            return create_demo_result(text)
        
        # Process input
        input_result = systems['input_coordinator'].process_input(
            text, InputType.TEXT
        )
        
        if not input_result.get('processing_successful'):
            return {'success': False, 'error': 'Failed to process text input'}
        
        # Safety check
        safety_check = systems['agents']['guardrail'].process({
            'content': input_result['extracted_text']
        })
        
        if not safety_check.get('success') or not safety_check.get('is_safe', True):
            return {'success': False, 'error': 'Content safety check failed'}
        
        # Parse problem
        parse_result = systems['agents']['parser'].process({
            'problem_text': input_result['extracted_text']
        })
        
        if not parse_result.get('success'):
            return {'success': False, 'error': 'Failed to parse problem'}
        
        # Check if parser flagged ambiguity -> trigger HITL
        if parse_result.get('needs_clarification', False):
            parse_result['hitl_trigger'] = 'parser_ambiguity'
        
        # Route strategy
        route_result = systems['agents']['router'].process({
            'problem_text': input_result['extracted_text'],
            'parsed_problem': parse_result
        })
        
        # Get relevant knowledge
        topic = parse_result.get('topic', 'general')
        knowledge = systems['rag_system'].get_knowledge_for_problem_type(topic, top_k=3)
        
        # Retrieve similar solved problems from memory (self-learning)
        similar_problems = []
        try:
            similar_problems = systems['memory_system'].find_similar_problems(
                input_result['extracted_text'], topic=topic, limit=3
            )
        except Exception as e:
            logger.debug(f"Memory retrieval skipped: {e}")
        
        # Build memory context for solver
        memory_context = ""
        if similar_problems:
            memory_context = "\n\nPreviously solved similar problems:\n"
            for sp in similar_problems:
                fb = sp.user_feedback
                fb_note = ""
                if fb and isinstance(fb, dict):
                    fb_note = f" (User feedback: {fb.get('feedback_type', 'none')})"
                memory_context += f"- Topic: {sp.problem_topic}, Solution: {sp.solution[:200]}{fb_note}\n"
        
        # Retrieve learning patterns for this topic
        learning_hints = ""
        try:
            patterns = systems['memory_system'].get_learning_patterns(pattern_type='solution_strategy')
            topic_patterns = [p for p in patterns if p.pattern_data.get('topic') == topic and p.success_rate > 0.6]
            if topic_patterns:
                learning_hints = "\n\nLearned strategies for this topic:\n"
                for p in topic_patterns[:3]:
                    learning_hints += f"- {p.pattern_data.get('description', 'Strategy')} (success rate: {p.success_rate:.0%})\n"
        except Exception as e:
            logger.debug(f"Learning patterns retrieval skipped: {e}")
        
        # Use MCP tools: attempt symbolic verification via registered tools
        mcp_context = ""
        mcp_web_results = []
        mcp_registry = systems.get('mcp_registry')
        if mcp_registry:
            try:
                # Try web search for additional context on hard problems
                web_result = mcp_registry.execute_tool("web_search", query=f"JEE math {topic} {input_result['extracted_text'][:80]}")
                if web_result.get('success') and web_result.get('result', {}).get('results'):
                    mcp_web_results = web_result['result']['results'][:2]
                    mcp_context = "\n\nWeb search references:\n"
                    for s in mcp_web_results:
                        mcp_context += f"- {s.get('title', '')}: {s.get('snippet', '')[:150]}\n"
            except Exception as e:
                logger.debug(f"MCP web search skipped: {e}")
        
        # Solve problem with memory context
        solve_result = systems['agents']['solver'].process({
            'problem_text': input_result['extracted_text'],
            'parsed_problem': parse_result,
            'solution_strategy': route_result.get('primary_strategy'),
            'relevant_knowledge': knowledge,
            'memory_context': memory_context + learning_hints + mcp_context
        })
        
        # Verify solution
        verify_result = systems['agents']['verifier'].process({
            'problem_text': input_result['extracted_text'],
            'solution': solve_result
        })
        
        # Generate explanation
        explain_result = systems['agents']['explainer'].process({
            'problem_text': input_result['extracted_text'],
            'solution': solve_result,
            'verification': verify_result
        })
        
        # Evaluate overall quality
        eval_result = systems['agents']['evaluator'].process({
            'problem_text': input_result['extracted_text'],
            'solution': solve_result,
            'verification': verify_result,
            'explanation': explain_result
        })
        
        return {
            'success': True,
            'input_result': input_result,
            'parse_result': parse_result,
            'route_result': route_result,
            'knowledge': knowledge,
            'similar_problems': similar_problems,
            'mcp_web_results': mcp_web_results,
            'solve_result': solve_result,
            'verify_result': verify_result,
            'explain_result': explain_result,
            'eval_result': eval_result,
            'agent_traces': [
                parse_result, route_result, solve_result,
                verify_result, explain_result, eval_result
            ]
        }
        
    except Exception as e:
        logger.error(f"Pipeline processing error: {e}")
        return {'success': False, 'error': str(e)}

def create_demo_result(text: str) -> Dict[str, Any]:
    """Create a demo result for testing UI"""
    return {
        'success': True,
        'input_result': {'extracted_text': text, 'processing_successful': True},
        'parse_result': {
            'success': True, 
            'topic': 'algebra',
            'agent': 'Parser Agent',
            'problem_structure': 'Quadratic equation'
        },
        'route_result': {
            'success': True,
            'agent': 'Intent Router Agent',
            'primary_strategy': 'algebraic_solution'
        },
        'solve_result': {
            'success': True,
            'agent': 'Solver Agent',
            'final_answer': 'x = 2, x = 3',
            'solution_steps': [
                {
                    'description': 'Apply quadratic formula',
                    'mathematical_work': 'x = (-b ± √(b²-4ac)) / 2a',
                    'reasoning': 'Standard method for solving quadratic equations'
                },
                {
                    'description': 'Substitute values',
                    'mathematical_work': 'x = (5 ± √(25-24)) / 2 = (5 ± 1) / 2',
                    'reasoning': 'Calculate discriminant and solve'
                }
            ],
            'confidence': 0.95
        },
        'verify_result': {
            'success': True,
            'agent': 'Verifier Agent',
            'is_correct': True,
            'confidence': 0.92,
            'issues_found': []
        },
        'explain_result': {
            'success': True,
            'agent': 'Explainer Agent',
            'conceptual_overview': 'This is a quadratic equation that can be solved using factoring or the quadratic formula.',
            'key_insights': [
                'The discriminant is positive, so there are two real solutions',
                'Both solutions can be verified by substituting back into the original equation'
            ],
            'common_mistakes': [
                'Forgetting to check both solutions',
                'Sign errors when applying the quadratic formula'
            ]
        },
        'eval_result': {
            'success': True,
            'agent': 'Evaluator Agent',
            'overall_quality': 'high'
        },
        'knowledge': [{
            'content': 'Quadratic equations have the form ax² + bx + c = 0 and can be solved using various methods including factoring, completing the square, and the quadratic formula.',
            'relevance_score': 0.9
        }],
        'agent_traces': [
            {'agent': 'Parser Agent', 'success': True, 'topic': 'algebra'},
            {'agent': 'Intent Router Agent', 'success': True, 'strategy': 'algebraic_solution'},
            {'agent': 'Solver Agent', 'success': True, 'final_answer': 'x = 2, x = 3'},
            {'agent': 'Verifier Agent', 'success': True, 'is_correct': True},
            {'agent': 'Explainer Agent', 'success': True},
            {'agent': 'Evaluator Agent', 'success': True}
        ]
    }

def process_image_input(image_data, systems: Dict) -> Dict[str, Any]:
    """Process image input through OCR and agent pipeline"""
    try:
        if not systems.get('modules_loaded', True):
            # Demo mode - extract some demo text
            demo_text = "Solve the equation: x² - 5x + 6 = 0"
            return create_demo_result(demo_text)
        
        # Process image through OCR
        input_result = systems['input_coordinator'].process_input(
            image_data, InputType.IMAGE
        )
        
        if not input_result.get('processing_successful'):
            return {'success': False, 'error': 'Failed to extract text from image'}
        
        # Continue with text processing pipeline
        return process_text_input(input_result['extracted_text'], systems)
        
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        return {'success': False, 'error': str(e)}

def process_audio_input(audio_data, systems: Dict) -> Dict[str, Any]:
    """Process audio input through speech-to-text and agent pipeline"""
    try:
        if not systems.get('modules_loaded', True):
            # Demo mode - simulate audio transcription
            demo_text = "What is the derivative of x squared plus 3x minus 2?"
            return create_demo_result(demo_text)
        
        # Process audio through speech-to-text
        input_result = systems['input_coordinator'].process_input(
            audio_data, InputType.AUDIO
        )
        
        if not input_result.get('processing_successful'):
            return {'success': False, 'error': 'Failed to transcribe audio'}
        
        # Continue with text processing pipeline
        return process_text_input(input_result['extracted_text'], systems)
        
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        return {'success': False, 'error': str(e)}

# Cached audio processor - loaded once, reused every call (no model reload delay)
_cached_audio_processor = None

def _get_audio_processor():
    global _cached_audio_processor
    if _cached_audio_processor is None:
        from src.input_processing.audio_processor import AudioProcessor
        _cached_audio_processor = AudioProcessor()
    return _cached_audio_processor

# Cached OCR processor - Tesseract + OpenCV, loaded once
_cached_ocr_processor = None

def _get_ocr_processor():
    global _cached_ocr_processor
    if _cached_ocr_processor is None:
        from src.input_processing.ocr_processor import OCRProcessor
        _cached_ocr_processor = OCRProcessor()
    return _cached_ocr_processor

def extract_text_from_image(image_file) -> Dict[str, Any]:
    """Tesseract OCR extraction with OpenCV preprocessing for math images"""
    try:
        from PIL import Image
        import numpy as np
        
        # Open image and ensure proper format
        pil_image = Image.open(image_file)
        
        # Handle all image modes (RGBA, palette, grayscale, etc.)
        if pil_image.mode == 'RGBA':
            # Composite onto white background for transparency
            bg = Image.new('RGB', pil_image.size, (255, 255, 255))
            bg.paste(pil_image, mask=pil_image.split()[3])
            pil_image = bg
        elif pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        np_image = np.array(pil_image)
        
        # Validate image has actual content
        if np_image.size == 0 or np_image.shape[0] < 10 or np_image.shape[1] < 10:
            return {'success': False, 'error': 'Image too small to extract text'}
        
        # Use cached OCR processor (Tesseract + OpenCV preprocessing)
        ocr = _get_ocr_processor()
        result = ocr.extract_text_with_confidence(np_image)
        
        text = result.get('extracted_text', '').strip()
        if text:
            return {'success': True, 'text': text, 'confidence': result.get('overall_confidence', 0)}
        return {'success': False, 'error': 'No text found in image'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def transcribe_audio_only(audio_data, systems: Dict) -> Dict[str, Any]:
    """Ultra-fast voice-to-text: cached model, zero overhead"""
    try:
        if not systems.get('modules_loaded', True):
            return {'success': True, 'extracted_text': "What is the derivative of x squared plus 3x minus 2?"}
        
        proc = _get_audio_processor()
        if not proc.is_available():
            return {'success': False, 'error': 'Whisper not loaded'}
        
        result = proc.process_audio(audio_data)
        
        if result.get('success') and result.get('text'):
            return {'success': True, 'extracted_text': result['text'].strip(), 'confidence': result.get('confidence', 0.0)}
        return {'success': False, 'error': result.get('error', 'No speech detected')}
        
    except Exception as e:
        logger.error(f"Audio transcription error: {e}")
        return {'success': False, 'error': str(e)}

def _find_brace_group(text: str, start: int) -> tuple:
    """Find matching {} group starting at position start. Returns (content, end_pos) or (None, start)."""
    if start >= len(text) or text[start] != '{':
        return None, start
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start+1:i], i + 1
    return None, start

def clean_latex_to_unicode(text: str) -> str:
    """Convert LaTeX to clean Unicode mathematical notation for display"""
    import re
    if not text:
        return text

    # ── Phase 1: Structural patterns (regex-based, before simple replacements) ──

    # \boxed{content} → content
    text = re.sub(r'\\boxed\{([^}]*)\}', r'\1', text)

    # \text{...}, \mathrm{...}, \mathbf{...}, \mathit{...}, \operatorname{...} → content
    text = re.sub(r'\\(?:text|mathrm|mathbf|mathit|operatorname)\{([^}]*)\}', r'\1', text)

    # \mathbb{R} etc. before brace removal
    mathbb_map = {'R': 'ℝ', 'Z': 'ℤ', 'N': 'ℕ', 'C': 'ℂ', 'Q': 'ℚ'}
    text = re.sub(r'\\mathbb\{([A-Z])\}', lambda m: mathbb_map.get(m.group(1), m.group(1)), text)

    # \frac{num}{den} → num/den  (handles nested braces)
    while '\\frac' in text:
        idx = text.index('\\frac')
        after = idx + 5  # skip \frac
        # skip optional whitespace
        while after < len(text) and text[after] == ' ':
            after += 1
        num, pos_after_num = _find_brace_group(text, after)
        if num is None:
            text = text[:idx] + text[idx+5:]
            continue
        den, pos_after_den = _find_brace_group(text, pos_after_num)
        if den is None:
            text = text[:idx] + num + text[pos_after_num:]
            continue
        # Clean simple single-char fracs: a/b, multi-char: (a)/(b)
        num_clean = num.strip()
        den_clean = den.strip()
        if len(num_clean) <= 1 and len(den_clean) <= 1:
            frac_str = f"{num_clean}/{den_clean}"
        elif len(num_clean) <= 3 and len(den_clean) <= 3 and ' ' not in num_clean and ' ' not in den_clean:
            frac_str = f"{num_clean}/{den_clean}"
        else:
            frac_str = f"({num_clean})/({den_clean})"
        text = text[:idx] + frac_str + text[pos_after_den:]

    # \sqrt[n]{expr} → ⁿ√(expr)  and  \sqrt{expr} → √(expr)
    sup_map_small = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', 'n': 'ⁿ'}
    text = re.sub(r'\\sqrt\[([^\]]+)\]\{([^}]*)\}',
                  lambda m: ''.join(sup_map_small.get(c, c) for c in m.group(1)) + '√(' + m.group(2) + ')', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', text)

    # \lim_{x \to a} → lim(x→a)
    text = re.sub(r'\\lim_\{([^}]*)\}', r'lim(\1)', text)
    text = re.sub(r'\\lim\b', 'lim', text)

    # \log, \ln, \sin, \cos, \tan, \sec, \csc, \cot, \arcsin, \arccos, \arctan
    for fn in ['arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh', 'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'log', 'ln', 'exp', 'det', 'max', 'min', 'gcd', 'lcm']:
        text = text.replace(f'\\{fn}', fn)

    # \left( \right) → ( )   \left[ \right] → [ ]
    text = re.sub(r'\\left\s*([(\[|{])', r'\1', text)
    text = re.sub(r'\\right\s*([)\]|}])', r'\1', text)
    text = re.sub(r'\\left\s*\\.', '', text)  # \left.
    text = re.sub(r'\\right\s*\\.', '', text)  # \right.

    # \binom{n}{k} → C(n,k)
    text = re.sub(r'\\binom\{([^}]*)\}\{([^}]*)\}', r'C(\1,\2)', text)

    # \overline{x} → x̄
    text = re.sub(r'\\overline\{([^}]*)\}', r'\1̄', text)

    # \vec{x} → x⃗
    text = re.sub(r'\\vec\{([^}]*)\}', r'\1⃗', text)

    # ── Phase 2: Simple symbol replacements (LONGEST-FIRST to prevent partial matches) ──
    replacements = {
        '\\rightarrow': '→', '\\leftarrow': '←', '\\Rightarrow': '⇒', '\\Leftarrow': '⇐',
        '\\longrightarrow': '→', '\\implies': '⇒',
        '\\qquad': '    ', '\\quad': '  ', '\\,': ' ', '\\;': ' ', '\\!': '',
        '\\infty': '∞', '\\infinity': '∞',
        '\\notin': '∉', '\\subset': '⊂', '\\supset': '⊃',
        '\\subseteq': '⊆', '\\supseteq': '⊇',
        '\\approx': '≈', '\\equiv': '≡', '\\cong': '≅', '\\simeq': '≃',
        '\\times': '×', '\\cdot': '·', '\\ldots': '…', '\\cdots': '⋯', '\\dots': '…',
        '\\prime': '′',
        '\\angle': '∠', '\\degree': '°', '\\circ': '°',
        '\\perp': '⊥', '\\parallel': '∥',
        '\\triangle': '△', '\\square': '□',
        '\\forall': '∀', '\\exists': '∃', '\\nexists': '∄',
        '\\nabla': '∇', '\\partial': '∂',
        '\\int': '∫', '\\iint': '∬', '\\iiint': '∭', '\\oint': '∮',
        '\\sum': '∑', '\\prod': '∏',
        '\\leq': '≤', '\\geq': '≥', '\\neq': '≠', '\\ne': '≠',
        '\\le': '≤', '\\ge': '≥',
        '\\div': '÷', '\\pm': '±', '\\mp': '∓',
        '\\cup': '∪', '\\cap': '∩', '\\in': '∈',
        '\\iff': '⇔', '\\to': '→',
        '\\pi': 'π', '\\theta': 'θ', '\\alpha': 'α', '\\beta': 'β',
        '\\gamma': 'γ', '\\delta': 'δ', '\\Delta': 'Δ', '\\epsilon': 'ε', '\\varepsilon': 'ε',
        '\\zeta': 'ζ', '\\eta': 'η', '\\kappa': 'κ',
        '\\lambda': 'λ', '\\Lambda': 'Λ', '\\mu': 'μ', '\\nu': 'ν',
        '\\xi': 'ξ', '\\Xi': 'Ξ',
        '\\rho': 'ρ', '\\sigma': 'σ', '\\Sigma': 'Σ',
        '\\tau': 'τ', '\\upsilon': 'υ',
        '\\phi': 'φ', '\\varphi': 'φ', '\\Phi': 'Φ',
        '\\chi': 'χ', '\\psi': 'ψ', '\\Psi': 'Ψ',
        '\\omega': 'ω', '\\Omega': 'Ω',
    }
    # Sort by key length descending so \infty matches before \in, \int before \in, etc.
    for latex, uni in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(latex, uni)

    # ── Phase 3: Superscripts and subscripts ──
    sup_map = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
               '+': '⁺', '-': '⁻', '=': '⁼', '(': '⁽', ')': '⁾',
               'n': 'ⁿ', 'i': 'ⁱ', 'x': 'ˣ', 'a': 'ᵃ', 'b': 'ᵇ', 'c': 'ᶜ', 'e': 'ᵉ', 'k': 'ᵏ', 't': 'ᵗ'}
    def to_superscript(m):
        return ''.join(sup_map.get(c, c) for c in m.group(1))
    # ^{...} with braces
    text = re.sub(r'\^{([^}]*)}', to_superscript, text)
    # ^single_char
    text = re.sub(r'\^([0-9a-zA-Z])', lambda m: sup_map.get(m.group(1), '^' + m.group(1)), text)

    sub_map = {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
               '+': '₊', '-': '₋', '=': '₌', '(': '₍', ')': '₎',
               'n': 'ₙ', 'i': 'ᵢ', 'j': 'ⱼ', 'k': 'ₖ', 'x': 'ₓ', 'a': 'ₐ', 'e': 'ₑ', 'o': 'ₒ', 'r': 'ᵣ', 's': 'ₛ', 't': 'ₜ'}
    def to_subscript(m):
        return ''.join(sub_map.get(c, c) for c in m.group(1))
    # _{...} with braces
    text = re.sub(r'_{([^}]*)}', to_subscript, text)
    # _single_char
    text = re.sub(r'_([0-9a-zA-Z])', lambda m: sub_map.get(m.group(1), '_' + m.group(1)), text)

    # ── Phase 4: Cleanup ──
    # Remove any remaining \command sequences
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # Remove stray braces (but keep parentheses)
    text = text.replace('{', '').replace('}', '')
    # Normalize whitespace
    text = re.sub(r'[ \t]{3,}', '  ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def render_solution_display(result: Dict[str, Any], systems: Dict):
    """Render solution in two-column layout matching the design spec"""
    if not result.get('success'):
        st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        return
    
    solve_result = result.get('solve_result', {})
    verify_result = result.get('verify_result', {})
    explain_result = result.get('explain_result', {})
    parse_result = result.get('parse_result', {})
    knowledge = result.get('knowledge', [])
    
    # ===== SECTION HEADER =====
    st.markdown("## 🎯 Solution")
    
    # ===== TWO COLUMN LAYOUT =====
    col_left, col_right = st.columns([2.5, 1])
    
    # ==================== LEFT COLUMN ====================
    with col_left:
        # --- Problem Box ---
        problem_text = result.get('input_result', {}).get('extracted_text', '')
        if problem_text:
            clean_problem = clean_latex_to_unicode(problem_text)
            st.markdown(f"""
            <div style="background: #1e1e2e; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 1rem;">
                <span style="color: #9ca3af; font-size: 0.85rem; font-weight: 600;">Problem:</span>
                <div style="color: #e0e0e0; font-size: 1.1rem; margin-top: 0.4rem; font-family: 'Cambria Math', 'STIX Two Math', 'Segoe UI', serif; line-height: 1.6;">
                    {clean_problem}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # --- Answer Box ---
        st.markdown("**Answer:**")
        final_answer = solve_result.get('final_answer', 'No answer generated')
        clean_answer = clean_latex_to_unicode(final_answer)
        st.markdown(f"""
        <div style="background: #1a1a2e; border-left: 4px solid #4ade80; border-radius: 8px; padding: 1rem 1.2rem; margin-bottom: 1.2rem;">
            <div style="color: #f0f0f0; font-size: 1.4rem; font-weight: 600; font-family: 'Cambria Math', 'STIX Two Math', 'Segoe UI', serif; line-height: 1.6;">
                {clean_answer}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- Solution Steps ---
        solution_steps = solve_result.get('solution_steps', [])
        if solution_steps:
            st.markdown("**Solution Steps:**")
            for i, step in enumerate(solution_steps, 1):
                desc = step.get('description', 'Calculation Step')
                with st.expander(f"Step {i}: {desc}...", expanded=(i == 1)):
                    st.markdown("**Work:**")
                    math_work = clean_latex_to_unicode(step.get('mathematical_work', ''))
                    if math_work:
                        st.markdown(f"""<div style="font-family: 'Cambria Math', 'STIX Two Math', 'Latin Modern Math', 'Segoe UI', serif;
                            font-size: 1.15rem; color: #e8e8e8; padding: 0.5rem 0.8rem; background: #1a1a2e;
                            border-radius: 6px; margin: 0.4rem 0; line-height: 1.6; white-space: pre-wrap;">{math_work}</div>""",
                            unsafe_allow_html=True)
                    reasoning = step.get('reasoning', '')
                    if reasoning:
                        st.markdown(f"**Reasoning:** {clean_latex_to_unicode(reasoning)}")
        
        # --- Key Insights ---
        if explain_result.get('success'):
            insights = explain_result.get('key_insights', [])
            if insights:
                st.markdown("**💡 Key Insights:**")
                for insight in insights:
                    st.markdown(f"• {clean_latex_to_unicode(insight)}")
            
            mistakes = explain_result.get('common_mistakes', [])
            if mistakes:
                st.markdown("**⚠️ Common Mistakes:**")
                for mistake in mistakes:
                    st.markdown(f"• {clean_latex_to_unicode(mistake)}")
    
    # ==================== RIGHT COLUMN ====================
    with col_right:
        # --- Topic ---
        topic = parse_result.get('topic', 'general')
        topic_icons = {
            'algebra': '📘', 'calculus': '📗', 'trigonometry': '📙',
            'geometry': '📐', 'probability': '🎲', 'statistics': '📊',
            'matrices': '🔢', 'vectors': '📏', 'complex_numbers': '🔮',
            'general': '📚'
        }
        icon = topic_icons.get(topic, '📚')
        st.markdown(f"""
        <div style="margin-bottom: 0.5rem;">
            <span style="color: #9ca3af; font-size: 0.85rem; font-weight: 600;">Topic:</span>
        </div>
        <div style="background: #1e293b; border-radius: 8px; padding: 0.5rem 0.8rem; margin-bottom: 1rem; display: inline-block;">
            <span style="font-size: 1rem;">{icon} {topic}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # --- Knowledge Used ---
        st.markdown(f"""
        <div style="margin-bottom: 0.3rem;">
            <span style="color: #9ca3af; font-size: 0.85rem; font-weight: 600;">📚 Knowledge Used:</span>
        </div>
        """, unsafe_allow_html=True)
        if knowledge:
            with st.expander(f"✨ {len(knowledge)} sources retrieved", expanded=False):
                for i, k in enumerate(knowledge, 1):
                    content = k.get('content', '')
                    score = k.get('relevance_score', 0)
                    if len(content) > 200:
                        content = content[:200] + "..."
                    st.markdown(f"**Source {i}** (Score: {score:.2f})")
                    st.markdown(f"<small>{content}</small>", unsafe_allow_html=True)
        else:
            st.markdown("No knowledge sources used")
        
        # --- Verification ---
        st.markdown(f"""
        <div style="margin-top: 0.8rem; margin-bottom: 0.3rem;">
            <span style="color: #9ca3af; font-size: 0.85rem; font-weight: 600;">Verification:</span>
        </div>
        """, unsafe_allow_html=True)
        is_correct = verify_result.get('is_correct', False)
        confidence = verify_result.get('confidence', 0)
        if is_correct:
            st.markdown(f"""
            <div style="background: #166534; border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem;">
                <span style="color: #4ade80;">☑️ Correct</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #7c2d12; border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem;">
                <span style="color: #fb923c;">⚠️ Needs Review</span>
            </div>
            """, unsafe_allow_html=True)
        
        # --- Confidence ---
        st.markdown(f"**Confidence:** {confidence*100:.0f}%")
        
        # --- Show Raw AI Response ---
        show_raw = st.checkbox("🔧 Show Raw AI Response", key="show_raw_response")
        if show_raw:
            with st.expander("AI Output (Unicode)", expanded=True):
                # --- Solver output ---
                st.markdown("**🧮 Solver:**")
                raw_answer = solve_result.get('final_answer', '')
                if raw_answer:
                    st.markdown(f"**Answer:** {clean_latex_to_unicode(raw_answer)}")
                raw_steps = solve_result.get('solution_steps', [])
                for si, stp in enumerate(raw_steps, 1):
                    desc = clean_latex_to_unicode(stp.get('description', ''))
                    work = clean_latex_to_unicode(stp.get('mathematical_work', ''))
                    reason = clean_latex_to_unicode(stp.get('reasoning', ''))
                    st.markdown(f"Step {si}: {desc}")
                    if work:
                        st.code(work, language=None)
                    if reason:
                        st.caption(reason)
                raw_verify = solve_result.get('verification', '')
                if raw_verify:
                    st.markdown(f"**Verification:** {clean_latex_to_unicode(raw_verify)}")
                
                st.markdown("---")
                # --- Verifier output ---
                st.markdown("**✅ Verifier:**")
                st.markdown(f"Correct: {verify_result.get('is_correct', 'N/A')}  |  Confidence: {verify_result.get('confidence', 0)*100:.0f}%")
                v_method = verify_result.get('verification_method', '')
                if v_method:
                    st.markdown(f"Method: {clean_latex_to_unicode(v_method)}")
                v_issues = verify_result.get('issues_found', [])
                if v_issues:
                    for iss in v_issues:
                        st.markdown(f"- {clean_latex_to_unicode(iss)}")
                
                st.markdown("---")
                # --- Explainer output ---
                st.markdown("**📖 Explainer:**")
                e_insights = explain_result.get('key_insights', [])
                if e_insights:
                    for ins in e_insights:
                        st.markdown(f"- {clean_latex_to_unicode(ins)}")
                e_mistakes = explain_result.get('common_mistakes', [])
                if e_mistakes:
                    st.markdown("Common mistakes:")
                    for mis in e_mistakes:
                        st.markdown(f"- {clean_latex_to_unicode(mis)}")
        
        # --- Show AI Workflow ---
        if st.button("🔄 Show AI Workflow", key="show_workflow_btn", use_container_width=True):
            st.session_state.show_workflow = not st.session_state.get('show_workflow', False)
        
        if st.session_state.get('show_workflow', False):
            traces = result.get('agent_traces', [])
            agent_names = ["Parser", "Router", "Solver", "Verifier", "Explainer", "Evaluator"]
            for i, name in enumerate(agent_names):
                if i < len(traces):
                    trace = traces[i]
                    icon = "✅" if trace.get('success', False) else "❌"
                    st.markdown(f"{icon} **{name}**")
                else:
                    st.markdown(f"⏳ **{name}**")
            # Show MCP tool usage
            mcp_refs = result.get('mcp_web_results')
            if mcp_refs:
                st.markdown("🔧 **MCP Web Search** — external references retrieved")
                for ref in mcp_refs[:3]:
                    st.markdown(f"  - [{ref.get('title','')}]({ref.get('url','')})" if ref.get('url') else f"  - {ref.get('title','')}")
        
        # --- Feedback ---
        st.markdown(f"""
        <div style="margin-top: 1rem; margin-bottom: 0.3rem;">
            <span style="color: #9ca3af; font-size: 0.85rem; font-weight: 600;">Feedback:</span>
        </div>
        """, unsafe_allow_html=True)
        col_fb1, col_fb2 = st.columns(2)
        with col_fb1:
            if st.button("👍 Helpful", key="fb_helpful", use_container_width=True):
                try:
                    feedback_record = FeedbackRecord(
                        id=str(uuid.uuid4()),
                        interaction_id=getattr(st.session_state, 'current_interaction_id', 'unknown'),
                        feedback_type='helpful',
                        original_text=problem_text,
                        corrected_text=None,
                        quality_rating={'overall': 'helpful'},
                        comments={}
                    )
                    systems['memory_system'].store_feedback(feedback_record)
                    st.success("Thanks!")
                except Exception:
                    st.success("Thanks!")
        with col_fb2:
            if st.button("👎 Not Helpful", key="fb_not_helpful", use_container_width=True):
                try:
                    feedback_record = FeedbackRecord(
                        id=str(uuid.uuid4()),
                        interaction_id=getattr(st.session_state, 'current_interaction_id', 'unknown'),
                        feedback_type='not_helpful',
                        original_text=problem_text,
                        corrected_text=None,
                        quality_rating={'overall': 'not_helpful'},
                        comments={}
                    )
                    systems['memory_system'].store_feedback(feedback_record)
                    st.warning("We'll improve!")
                except Exception:
                    st.warning("We'll improve!")

def render_hitl_interface(result: Dict[str, Any], systems: Dict):
    """Render professional Human-in-the-Loop feedback interface"""
    solve_result = result.get('solve_result', {})
    verify_result = result.get('verify_result', {})
    extracted_text = result.get('input_result', {}).get('extracted_text', '')
    current_solution = solve_result.get('final_answer', '')
    
    # Convert to Unicode for display
    display_problem = clean_latex_to_unicode(extracted_text)
    display_solution = clean_latex_to_unicode(current_solution)
    
    confidence = verify_result.get('confidence', 0)
    
    # ─── Section divider ───
    st.markdown("""
    <div style="margin: 2rem 0 1.5rem 0; border-top: 1px solid #2d2d3d; padding-top: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span style="font-size: 1.4rem;">🔄</span>
            <span style="font-size: 1.3rem; font-weight: 700; color: #f0f0f0;">Human-in-the-Loop Review</span>
        </div>
        <p style="color: #6b7280; font-size: 0.85rem; margin: 0.3rem 0 0 2.2rem;">
            Your feedback directly improves future solutions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── Two-column: Feedback form | Quick stats ───
    col_form, col_stats = st.columns([3, 1])
    
    with col_stats:
        # Quick assessment pills
        st.markdown("""
        <div style="background: #1e1e2e; border-radius: 10px; padding: 1rem; margin-bottom: 0.8rem;">
            <div style="font-size: 0.8rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.6rem;">Quick Stats</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Confidence", f"{confidence*100:.0f}%")
        
        steps_count = len(solve_result.get('solution_steps', []))
        st.metric("Solution Steps", str(steps_count))
        
        issues = len(verify_result.get('issues_found', []))
        st.metric("Issues Found", str(issues))
        
        # Accuracy indicator
        if confidence >= 0.9:
            acc_color, acc_label = "#10b981", "High"
        elif confidence >= 0.7:
            acc_color, acc_label = "#f59e0b", "Medium"
        else:
            acc_color, acc_label = "#ef4444", "Low"
        
        st.markdown(f"""
        <div style="background: #1e1e2e; border-radius: 8px; padding: 0.8rem; margin-top: 0.5rem; text-align: center;">
            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Reliability</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: {acc_color}; margin-top: 0.3rem;">● {acc_label}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_form:
        with st.form("hitl_feedback_enhanced", clear_on_submit=True):
            # ── Rating row ──
            st.markdown("""
            <div style="font-size: 0.8rem; color: #9ca3af; font-weight: 600; text-transform: uppercase; 
                        letter-spacing: 0.05em; margin-bottom: 0.4rem;">Rate This Solution</div>
            """, unsafe_allow_html=True)
            
            r1, r2, r3 = st.columns(3)
            with r1:
                solution_rating = st.select_slider(
                    "Accuracy", options=["Poor", "Fair", "Good", "Excellent"], value="Good",
                    key="solution_quality"
                )
            with r2:
                explanation_rating = st.select_slider(
                    "Clarity", options=["Poor", "Fair", "Good", "Excellent"], value="Good",
                    key="explanation_quality"
                )
            with r3:
                teaching_style = st.selectbox(
                    "Teaching Style",
                    ["Step-by-step", "Conceptual first", "Multiple methods", "Visual approach"],
                    key="teaching_style"
                )
            
            # ── Assessment ──
            feedback_type = st.radio(
                "Overall Assessment",
                ["✅ Approve", "✏️ Minor Fix", "🔄 Major Revision", "❌ Incorrect"],
                horizontal=True,
                key="feedback_type_enhanced"
            )
            
            # ── Correction fields (compact) ──
            c1, c2 = st.columns(2)
            with c1:
                corrected_problem = st.text_area(
                    "📝 Edit Problem (if needed)",
                    value=display_problem,
                    height=70,
                    key="corrected_problem"
                )
            with c2:
                corrected_solution = st.text_area(
                    "🧮 Correct Answer (if needed)",
                    value=display_solution,
                    height=70,
                    key="corrected_solution"
                )
            
            method_feedback = st.text_area(
                "💬 Feedback & Suggestions",
                placeholder="Suggest a better method, point out errors, or share learning notes...",
                height=70,
                key="method_feedback"
            )
            
            # ── Submit ──
            submit_feedback = st.form_submit_button(
                "Submit Feedback →",
                use_container_width=True
            )
            
            if submit_feedback:
                feedback_record = FeedbackRecord(
                    id=str(uuid.uuid4()),
                    interaction_id=getattr(st.session_state, 'current_interaction_id', 'unknown'),
                    feedback_type=feedback_type.split()[1].lower(),
                    original_text=extracted_text,
                    corrected_text=corrected_problem if corrected_problem != extracted_text else None,
                    quality_rating={
                        'solution': solution_rating,
                        'explanation': explanation_rating,
                        'overall': feedback_type
                    },
                    comments={
                        'method_feedback': method_feedback,
                        'teaching_style': teaching_style,
                        'corrected_solution': corrected_solution if corrected_solution != current_solution else None
                    }
                )
                
                success = systems['memory_system'].store_feedback(feedback_record)
                
                # Store as learning pattern for self-learning
                if success:
                    is_approved = 'approve' in feedback_type.lower()
                    topic = result.get('parse_result', {}).get('topic', 'general')
                    strategy = result.get('route_result', {}).get('primary_strategy', 'unknown')
                    try:
                        from src.storage.memory_system import LearningPattern
                        pattern = LearningPattern(
                            id=str(uuid.uuid4()),
                            pattern_type='solution_strategy',
                            pattern_data={
                                'topic': topic,
                                'strategy': strategy,
                                'description': f"{topic} solved via {strategy}",
                                'feedback': feedback_type
                            },
                            frequency=1,
                            success_rate=1.0 if is_approved else 0.0
                        )
                        systems['memory_system'].store_learning_pattern(pattern)
                    except Exception:
                        pass
                
                if success:
                    st.success("✅ Feedback saved — thank you!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Failed to save feedback")

def render_agent_traces(result: Dict[str, Any]):
    """Render agent execution traces"""
    with st.expander("🤖 Agent Execution Traces", expanded=False):
        traces = result.get('agent_traces', [])
        
        # Agent pipeline overview
        st.markdown("### 🔄 Multi-Agent Pipeline Execution")
        
        # Visual pipeline flow
        agent_names = ["Parser", "Router", "Solver", "Verifier", "Explainer", "Evaluator"]
        cols = st.columns(len(agent_names))
        
        for i, (col, agent_name) in enumerate(zip(cols, agent_names)):
            if i < len(traces):
                trace = traces[i]
                success = trace.get('success', False)
                status_icon = "✅" if success else "❌"
                col.markdown(f"""
                <div class="agent-trace">
                    <div class="agent-status">{status_icon}</div>
                    <div class="agent-name">{agent_name}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                cols[i].markdown(f"⏳ {agent_name}")
        
        # Detailed trace information
        st.markdown("---")
        st.markdown("### 📊 Detailed Agent Reports")
        
        for i, trace in enumerate(traces, 1):
            agent_name = trace.get('agent', f'Agent {i}')
            success = trace.get('success', False)
            
            with st.expander(f"{'✅' if success else '❌'} {agent_name} Report"):
                col_trace1, col_trace2 = st.columns([2, 1])
                
                with col_trace1:
                    if success:
                        # Show key outputs based on agent type
                        if 'topic' in trace:
                            st.markdown(f"**📚 Identified Topic:** {trace['topic']}")
                        if 'strategy' in trace:
                            st.markdown(f"**🎯 Strategy:** {trace['strategy']}")
                        if 'final_answer' in trace:
                            st.markdown(f"**📋 Answer:** {trace['final_answer']}")
                        if 'is_correct' in trace:
                            status = "Verified" if trace['is_correct'] else "Needs Review"
                            st.markdown(f"**🔍 Verification:** {status}")
                        
                        # Show processing time if available
                        if 'processing_time' in trace:
                            st.markdown(f"**⏱️ Processing Time:** {trace['processing_time']:.2f}s")
                    else:
                        error = trace.get('error', 'Unknown error')
                        st.error(f"**Error:** {error}")
                
                with col_trace2:
                    st.markdown("**📊 Agent Metrics**")
                    confidence = trace.get('confidence', 0.5)
                    st.metric("Confidence", f"{confidence*100:.1f}%")
                    
                    processing_time = trace.get('processing_time', 1.5)
                    st.metric("Time", f"{processing_time:.2f}s")
        
        # Pipeline summary
        st.markdown("---")
        st.markdown("### 📈 Pipeline Performance")
        
        col_perf1, col_perf2, col_perf3 = st.columns(3)
        
        successful_agents = sum(1 for trace in traces if trace.get('success', False))
        total_agents = len(traces)
        
        with col_perf1:
            st.metric("Success Rate", f"{successful_agents}/{total_agents}")
        
        with col_perf2:
            avg_confidence = sum(trace.get('confidence', 0) for trace in traces) / max(len(traces), 1)
            st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
        
        with col_perf3:
            total_time = sum(trace.get('processing_time', 1) for trace in traces)
            st.metric("Total Time", f"{total_time:.1f}s")

def render_knowledge_search(systems: Dict):
    """Render knowledge base search interface"""
    st.markdown("#### 📚 Knowledge Base Search")
    
    search_query = st.text_input(
        "Search mathematical concepts",
        placeholder="e.g., quadratic formula, derivatives, probability",
        key="kb_search"
    )
    
    if search_query:
        knowledge_results = systems['rag_system'].retrieve_relevant_knowledge(
            search_query, top_k=3
        )
        
        if knowledge_results:
            st.markdown("**Relevant Knowledge:**")
            for i, result in enumerate(knowledge_results, 1):
                with st.expander(f"Result {i} (Score: {result['relevance_score']:.2f})"):
                    content = result['content']
                    # Truncate long content
                    if len(content) > 500:
                        content = content[:500] + "..."
                    st.markdown(content)
        else:
            st.info("No relevant knowledge found")

def render_sidebar(systems: Dict):
    """Render sidebar with analytics and controls"""
    with st.sidebar:
        st.markdown("## 🎛️ Control Panel")
        
        # System status
        if not systems.get('modules_loaded', True):
            st.error("🚧 Demo Mode Active")
            st.info("Some modules are missing. Install dependencies for full functionality.")
        else:
            st.success("✅ All Systems Online")
        
        # Session info
        st.markdown("### 📊 Session Info")
        st.info(f"Session ID: {st.session_state.session_id[:8]}...")
        
        # LLM status
        if systems.get('modules_loaded', True):
            solver_agent = systems['agents']['solver']
            llm_status = "✅ Available" if getattr(solver_agent, 'llm_available', True) else "❌ Not Available"
            llm_provider = getattr(solver_agent, 'llm_provider', 'groq').upper()
        else:
            llm_status = "🚧 Demo Mode"
            llm_provider = "GROQ (Simulated)"
        
        st.markdown("### 🤖 AI Status")
        st.markdown(f"**LLM Provider:** {llm_provider}")
        st.markdown(f"**Status:** {llm_status}")
        
        # System stats
        stats = systems['rag_system'].get_knowledge_statistics()
        st.markdown("### 📈 System Stats")
        st.metric("Knowledge Documents", stats.get('total_documents', 8))
        st.metric("Storage Type", stats.get('storage_type', 'ChromaDB'))
        
        # Knowledge search
        render_knowledge_search(systems)
        
        # Reset session
        if st.button("🔄 New Session"):
            for key in list(st.session_state.keys()):
                if key != 'systems':  # Keep systems initialized
                    del st.session_state[key]
            st.rerun()

def main():
    """Main application function"""
    # Page configuration - MUST be first Streamlit command
    st.set_page_config(
        page_title="Math Mentor AI",
        page_icon="🧮",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_css()
    
    # Initialize systems with caching
    @st.cache_resource
    def get_systems():
        return initialize_systems()
    
    systems = get_systems()
    if not systems:
        st.error("❌ Failed to initialize Math Mentor AI systems")
        return
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    st.markdown("---")
    
    # ============ FULL WIDTH LAYOUT ============
    
    st.markdown("### 📝 Enter Your Math Problem")
    
    # Math symbols toolbar - FULL WIDTH
    render_math_symbols()
    
    st.markdown("---")
    
    # Quick examples - FULL WIDTH
    st.markdown("#### 🚀 Quick Examples:")
    
    # Row 1
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        if st.button("Quadratic", use_container_width=True, key="ex1"):
            st.session_state.problem_input = "Solve x² + 5x - 6 = 0"
    with col2:
        if st.button("Integral", use_container_width=True, key="ex2"):
            st.session_state.problem_input = "Find ∫ x² + 2x dx"
    with col3:
        if st.button("Derivative", use_container_width=True, key="ex3"):
            st.session_state.problem_input = "Find d/dx(x³ + 2x²)"
    with col4:
        if st.button("Trig", use_container_width=True, key="ex4"):
            st.session_state.problem_input = "Prove sin²(x) + cos²(x) = 1"
    with col5:
        if st.button("Limit", use_container_width=True, key="ex5"):
            st.session_state.problem_input = "lim(x→0) sin(x)/x"
    with col6:
        if st.button("Series", use_container_width=True, key="ex6"):
            st.session_state.problem_input = "Sum: 1+2+3+...+n"
    with col7:
        if st.button("Matrix", use_container_width=True, key="ex7"):
            st.session_state.problem_input = "Det[[1,2],[3,4]]"
    with col8:
        if st.button("Complex", use_container_width=True, key="ex8"):
            st.session_state.problem_input = "(3+4i)×(2-i)"
    
    st.markdown("---")
    
    # Voice & Image Input - Compact Professional Layout
    st.markdown("#### 🔊 Audio / 📷 Image Input (Optional):")
    
    col_audio, col_spacer, col_image = st.columns([3, 6, 3])
    
    with col_audio:
        st.markdown("**Record 🎤**")
        
        if AUDIO_RECORDER_AVAILABLE:
            # Compact professional white microphone icon
            audio_bytes = audio_recorder(
                text="",
                recording_color="#ff4b4b",
                neutral_color="#ffffff",
                icon_name="microphone",
                icon_size="2x",
                sample_rate=16000,
                pause_threshold=1.5,
                key="voice_recorder"
            )
            
            # Track to avoid reprocessing same audio
            if 'last_audio_hash' not in st.session_state:
                st.session_state.last_audio_hash = None
            
            if audio_bytes is not None and len(audio_bytes) > 0:
                import hashlib
                audio_hash = hashlib.md5(audio_bytes).hexdigest()
                
                if audio_hash != st.session_state.last_audio_hash:
                    st.session_state.last_audio_hash = audio_hash
                    
                    try:
                        fd, tmp_path = tempfile.mkstemp(suffix=".wav", prefix="v_")
                        _os.write(fd, audio_bytes)
                        _os.close(fd)
                        
                        result = transcribe_audio_only(tmp_path, systems)
                        
                        try:
                            _os.unlink(tmp_path)
                        except:
                            pass
                        
                        if result.get('success'):
                            txt = (
                                result.get('extracted_text') or
                                result.get('text') or
                                result.get('enhanced_text') or
                                result.get('original_text', '')
                            )
                            if txt and txt.strip():
                                st.session_state.problem_input = txt.strip()
                    except Exception:
                        pass
        else:
            st.info("Install: pip install audio-recorder-streamlit")
    
    with col_image:
        st.markdown("**📷 Image**")
        # Hide drag-and-drop text, file size, and upload icon - show only Browse button
        st.markdown("""
        <style>
        [data-testid="stFileUploader"] section > div:first-child {
            display: none !important;
        }
        [data-testid="stFileUploader"] section {
            padding: 0 !important;
        }
        [data-testid="stFileUploader"] section > button {
            width: 100% !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] {
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            min-height: 0 !important;
        }
        [data-testid="stFileUploaderDropzone"] div:has(> small) {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] small {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"] {
            display: none !important;
        }
        [data-testid="stFileUploaderDropzone"] svg {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        uploaded_image = st.file_uploader(
            "Browse",
            type=['png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff', 'gif'],
            key="img_upload",
            label_visibility="collapsed"
        )
        if uploaded_image:
            import hashlib
            img_bytes = uploaded_image.getvalue()
            img_hash = hashlib.sha256(img_bytes).hexdigest()
            uploaded_image.seek(0)
            
            if 'last_img_hash' not in st.session_state:
                st.session_state.last_img_hash = None
            
            if img_hash != st.session_state.last_img_hash:
                st.session_state.last_img_hash = img_hash
                # Force-clear ALL old state for fresh extraction
                st.session_state.processing_complete = False
                for key in ['current_result', 'hitl_submitted']:
                    if key in st.session_state:
                        del st.session_state[key]
                # Clear old problem text BEFORE extraction
                st.session_state['problem_input'] = ""
                
                extraction_done = False
                extracted_text = ""
                with st.spinner("🔍 Extracting text from image..."):
                    try:
                        result = extract_text_from_image(uploaded_image)
                        if result.get('success') and result.get('text'):
                            extracted_text = result['text']
                            extraction_done = True
                        else:
                            st.warning("⚠️ Could not extract text. Try a clearer image.")
                    except Exception as e:
                        st.error(f"❌ Extraction failed: {e}")
                
                if extraction_done:
                    st.session_state['problem_input'] = extracted_text
                    st.rerun()
    
    st.markdown("#### 📝 Type or Edit Your Problem:")
    
    # Main text input - uses session state key for dynamic updates from audio/image
    if 'problem_input' not in st.session_state:
        st.session_state.problem_input = ""
    
    problem_text = st.text_area(
        "",
        placeholder="Type your math problem here - supports LaTeX, Unicode, and plain text\n\n🎤 Record audio above to auto-populate this field\n📷 Upload image above to extract text automatically",
        height=300,
        key="problem_input",
        label_visibility="collapsed"
    )
    
    # Action buttons
    col_clear, col_solve = st.columns([1, 4])
    
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True, key="clear_btn"):
            st.session_state.problem_input = ""
            st.session_state.processing_complete = False
            if 'current_result' in st.session_state:
                del st.session_state.current_result
            st.rerun()
    
    with col_solve:
        if st.button("🧮 Solve Problem", type="primary", use_container_width=True, key="solve_btn"):
            if problem_text.strip():
                with st.spinner("� AI working..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔍 Analyzing problem...")
                    progress_bar.progress(20)
                    result = process_text_input(problem_text, systems)
                    
                    status_text.text("🧠 Running AI agents...")
                    progress_bar.progress(60)
                    time.sleep(0.4)
                    
                    status_text.text("✅ Solution complete!")
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.session_state.current_result = result
                    
                    if result.get('success'):
                        interaction = InteractionRecord(
                            id=str(uuid.uuid4()),
                            session_id=st.session_state.session_id,
                            input_type="text",
                            original_input=problem_text,
                            processed_input=result['input_result']['extracted_text'],
                            problem_topic=result['parse_result'].get('topic', 'unknown'),
                            agent_trace=result.get('agent_traces', []),
                            solution=result['solve_result'].get('final_answer', ''),
                            confidence_scores={
                                'solver': result['solve_result'].get('confidence', 0),
                                'verifier': result['verify_result'].get('confidence', 0)
                            }
                        )
                        
                        st.session_state.current_interaction_id = interaction.id
                        systems['memory_system'].store_interaction(interaction)
                        st.success("💾 Solution saved!")
                    
                    st.session_state.processing_complete = True
            else:
                st.warning("⚠️ Please enter a math problem or record audio first!")
    
    # Results section (full width) - shown ONLY after solving
    if st.session_state.processing_complete and 'current_result' in st.session_state:
        st.markdown("---")
        result = st.session_state.current_result
        
        # Display solution in two-column layout
        render_solution_display(result, systems)
        
        # HITL detailed feedback (below solution)
        if result.get('success'):
            # Re-check button (user-triggered HITL)
            st.markdown("""<div style="margin-top:1rem;"></div>""", unsafe_allow_html=True)
            if st.button("🔄 Re-check / Re-solve", key="recheck_btn", use_container_width=True):
                with st.spinner("Re-solving with fresh verification..."):
                    problem = result.get('input_result', {}).get('extracted_text', '')
                    fresh_result = process_text_input(problem, systems)
                    if fresh_result.get('success'):
                        st.session_state.current_result = fresh_result
                        st.rerun()
                    else:
                        st.error("Re-check failed. Please try again.")
            
            render_hitl_interface(result, systems)

if __name__ == "__main__":
    main()

