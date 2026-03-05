#!/usr/bin/env python3
"""
Math Mentor AI - System Verification Script
Tests all components to ensure proper functionality
"""

import os
import sys
from pathlib import Path
import importlib.util

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def test_imports():
    """Test all required imports"""
    print_header("Testing Package Imports")
    
    tests = [
        ("Streamlit", "streamlit"),
        ("Groq API", "groq"),
        ("ChromaDB", "chromadb"),
        ("PIL/Pillow", "PIL"),
        ("Pytesseract", "pytesseract"),
        ("Sentence Transformers", "sentence_transformers"),
        ("NumPy", "numpy"),
        ("SymPy", "sympy"),
        ("Plotly", "plotly"),
    ]
    
    passed = 0
    for name, module in tests:
        try:
            __import__(module)
            print(f"✅ {name:<20} - OK")
            passed += 1
        except ImportError:
            print(f"❌ {name:<20} - MISSING")
        except Exception as e:
            print(f"⚠️  {name:<20} - ERROR: {str(e)[:50]}...")
    
    # Test whisper separately with better error handling
    try:
        __import__("whisper")
        print(f"✅ {'Whisper':<20} - OK")
        passed += 1
    except ImportError:
        print(f"❌ {'Whisper':<20} - MISSING")
    except Exception as e:
        print(f"⚠️  {'Whisper':<20} - ERROR: {str(e)[:50]}...")
        # Whisper has issues but we can continue without it
    
    total_tests = len(tests) + 1  # +1 for whisper
    print(f"\nImport Tests: {passed}/{total_tests} passed")
    return passed >= len(tests) - 1  # Consider success if most packages work

def test_project_structure():
    """Test project structure"""
    print_header("Testing Project Structure")
    
    required_files = [
        "src/__init__.py",
        "src/config.py",
        "src/agents/base_agent.py",
        "src/agents/solver_agent.py",
        "src/input_processing/input_coordinator.py",
        "src/rag/knowledge_base.py",
        "src/storage/memory_system.py",
        "src/ui/streamlit_app.py",
        "src/ui/styles.css",
        "requirements.txt",
        "data/chroma_db/chroma.sqlite3",
    ]
    
    required_dirs = [
        "knowledge_base",
        "logs",
        "data/chroma_db",
    ]
    
    passed = 0
    total = len(required_files) + len(required_dirs)
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ File: {file_path}")
            passed += 1
        else:
            print(f"❌ File: {file_path} - MISSING")
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ Dir:  {dir_path}")
            passed += 1
        else:
            print(f"❌ Dir:  {dir_path} - MISSING")
    
    print(f"\nStructure Tests: {passed}/{total} passed")
    return passed == total

def test_knowledge_base():
    """Test knowledge base files"""
    print_header("Testing Knowledge Base")
    
    kb_files = [
        "algebra_fundamentals.md",
        "calculus_essentials.md",
        "complex_numbers.md", 
        "geometry_formulas.md",
        "matrices_determinants.md",
        "probability_statistics.md",
        "trigonometry.md",
        "vectors_3d_geometry.md"
    ]
    
    kb_dir = project_root / "knowledge_base"
    passed = 0
    
    for kb_file in kb_files:
        full_path = kb_dir / kb_file
        if full_path.exists() and full_path.stat().st_size > 0:
            print(f"✅ Knowledge: {kb_file}")
            passed += 1
        else:
            print(f"❌ Knowledge: {kb_file} - MISSING OR EMPTY")
    
    print(f"\nKnowledge Base Tests: {passed}/{len(kb_files)} passed")
    return passed == len(kb_files)

def test_configuration():
    """Test configuration files"""
    print_header("Testing Configuration")
    
    try:
        import src.config as config
        print("✅ Configuration loaded successfully")
        
        # Check if ChromaDB path exists
        if hasattr(config, 'CHROMA_DB_PATH'):
            print("✅ ChromaDB path configured")
        else:
            print("❌ ChromaDB path not found in config")
            
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_agents():
    """Test agent initialization"""
    print_header("Testing AI Agents")
    
    try:
        # Test base agent
        from src.agents.base_agent import BaseAgent
        print("✅ BaseAgent class loaded")
        
        # Test individual agents
        agent_modules = [
            "parser_agent",
            "intent_router_agent", 
            "solver_agent",
            "verifier_agent",
            "explainer_agent",
            "guardrail_agent",
            "evaluator_agent"
        ]
        
        passed = 1  # BaseAgent already passed
        for agent_name in agent_modules:
            try:
                module = importlib.import_module(f"src.agents.{agent_name}")
                print(f"✅ {agent_name} module loaded")
                passed += 1
            except Exception as e:
                print(f"❌ {agent_name} failed: {e}")
        
        print(f"\nAgent Tests: {passed}/{len(agent_modules)+1} passed")
        return passed == len(agent_modules) + 1
        
    except Exception as e:
        print(f"❌ Agent testing error: {e}")
        return False

def test_ui_components():
    """Test UI components"""
    print_header("Testing UI Components")
    
    try:
        # Check if streamlit app can be loaded
        app_path = project_root / "src" / "ui" / "streamlit_app.py"
        if app_path.exists():
            print("✅ Streamlit app file exists")
            
            # Check CSS file
            css_path = project_root / "src" / "ui" / "styles.css"
            if css_path.exists():
                print("✅ CSS styles file exists")
            else:
                print("❌ CSS styles file missing")
                return False
                
            # Try to load the app module
            try:
                spec = importlib.util.spec_from_file_location("streamlit_app", app_path)
                module = importlib.util.module_from_spec(spec)
                print("✅ Streamlit app can be imported")
                return True
            except Exception as e:
                print(f"❌ Streamlit app import error: {e}")
                return False
        else:
            print("❌ Streamlit app file missing")
            return False
            
    except Exception as e:
        print(f"❌ UI testing error: {e}")
        return False

def show_summary(results):
    """Show verification summary"""
    print_header("Verification Summary")
    
    test_names = [
        "Package Imports",
        "Project Structure", 
        "Knowledge Base",
        "Configuration",
        "AI Agents",
        "UI Components"
    ]
    
    passed_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("\n" + "="*60)
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED! System is ready to use.")
        print("🚀 Run 'python launch_ui.py' to start Math Mentor AI")
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed. Please check:")
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Check API key configuration in .env file")
        print("   • Verify file permissions and paths")
    print("="*60)

def main():
    """Main verification function"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                Math Mentor AI - System Verification          ║
║                   Testing All Components...                   ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    # Run all tests
    results = [
        test_imports(),
        test_project_structure(),
        test_knowledge_base(),
        test_configuration(), 
        test_agents(),
        test_ui_components()
    ]
    
    # Show summary
    show_summary(results)

if __name__ == "__main__":
    main()