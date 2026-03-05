# -*- coding: utf-8 -*-
"""
Multimodal Math Mentor - Main Entry Point
A RAG + Multi-Agent system for solving JEE-style math problems
with Human-in-the-Loop feedback and self-learning capabilities
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.ui.streamlit_app import main as run_app

if __name__ == "__main__":
    run_app()