#!/usr/bin/env python3
"""
DeepResearch WebUI - Main Application
A comprehensive web interface for configuring, running, and monitoring research tasks.
"""

import streamlit as st
import sys
import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import research components
try:
    # Try importing the research components we'll need later
    import sys
    import os
    inference_path = os.path.join(os.path.dirname(__file__), '..', 'inference')
    if inference_path not in sys.path:
        sys.path.append(inference_path)
except ImportError:
    pass  # Will handle in task manager when needed

from webui.utils.task_manager import TaskManager
from webui.utils.config_manager import ConfigManager
from webui.components import sidebar, main_content, task_status

def init_session_state():
    """Initialize session state variables"""
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    if 'config_manager' not in st.session_state:
        st.session_state.config_manager = ConfigManager()
    
    if 'current_task' not in st.session_state:
        st.session_state.current_task = None
    
    if 'task_results' not in st.session_state:
        st.session_state.task_results = []

def main():
    """Main application entry point"""
    
    # Configure page
    st.set_page_config(
        page_title="DeepResearch WebUI",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .task-card {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .status-running {
        color: #ff9800;
    }
    .status-completed {
        color: #4caf50;
    }
    .status-error {
        color: #f44336;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 DeepResearch WebUI</h1>
        <p>Configure parameters, control research tasks, and view results</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration and controls
    with st.sidebar:
        sidebar.render_sidebar()
    
    # Main content area
    main_content.render_main_content()
    
    # Auto-refresh for task status updates
    if st.session_state.current_task and st.session_state.current_task.get('status') == 'running':
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    main()