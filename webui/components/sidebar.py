"""
Sidebar component for configuration and controls
"""

import streamlit as st
import json
from typing import Dict, Any


def render_sidebar():
    """Render the sidebar with configuration options"""
    
    st.title("⚙️ Configuration")
    
    # Configuration tabs
    config_tab, env_tab, tools_tab = st.tabs(["Model Config", "Environment", "Tools"])
    
    with config_tab:
        render_model_config()
    
    with env_tab:
        render_environment_config()
    
    with tools_tab:
        render_tools_config()
    
    st.divider()
    
    # Task controls
    st.title("🎮 Task Controls")
    render_task_controls()


def render_model_config():
    """Render model configuration section"""
    config_manager = st.session_state.config_manager
    
    st.subheader("Model Settings")
    
    # Model selection
    model_options = config_manager.get_model_options()
    selected_model = st.selectbox(
        "Model",
        model_options,
        index=model_options.index('qwen-plus') if 'qwen-plus' in model_options else 0,
        help="Select the language model for research tasks"
    )
    
    # Generation parameters
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.6,
            step=0.1,
            help="Controls randomness in model outputs"
        )
        
        top_p = st.slider(
            "Top-p",
            min_value=0.0,
            max_value=1.0,
            value=0.95,
            step=0.05,
            help="Nucleus sampling parameter"
        )
    
    with col2:
        presence_penalty = st.slider(
            "Presence Penalty",
            min_value=0.0,
            max_value=2.0,
            value=1.1,
            step=0.1,
            help="Penalize repeated tokens"
        )
        
        max_retries = st.number_input(
            "Max Retries",
            min_value=1,
            max_value=20,
            value=10,
            help="Maximum API call retries"
        )
    
    # Execution settings
    st.subheader("Execution Settings")
    
    col3, col4 = st.columns(2)
    
    with col3:
        max_workers = st.number_input(
            "Max Workers",
            min_value=1,
            max_value=50,
            value=20,
            help="Maximum concurrent workers"
        )
    
    with col4:
        rollout_count = st.number_input(
            "Rollout Count",
            min_value=1,
            max_value=10,
            value=3,
            help="Number of rollouts per task"
        )
    
    # Store configuration in session state
    st.session_state.model_config = {
        'model': selected_model,
        'temperature': temperature,
        'top_p': top_p,
        'presence_penalty': presence_penalty,
        'max_retries': max_retries,
        'max_workers': max_workers,
        'rollout_count': rollout_count,
        'max_input_tokens': 320000  # Fixed for now
    }


def render_environment_config():
    """Render environment configuration section"""
    config_manager = st.session_state.config_manager
    env_config = config_manager.load_env_config()
    
    st.subheader("API Keys & Environment")
    
    # API Keys
    serper_key = st.text_input(
        "Serper API Key",
        value=env_config.get('serper_key_id', ''),
        type='password',
        help="Required for web search functionality"
    )
    
    jina_key = st.text_input(
        "Jina API Key",
        value=env_config.get('jina_api_keys', ''),
        type='password',
        help="Required for web page reading"
    )
    
    dashscope_key = st.text_input(
        "DashScope API Key",
        value=env_config.get('dashscope_api_key', ''),
        type='password',
        help="Required for file parsing and some models"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_key = st.text_input(
            "OpenAI API Key",
            value=env_config.get('api_key', ''),
            type='password',
            help="Alternative to DashScope for some models"
        )
    
    with col2:
        api_base = st.text_input(
            "API Base URL",
            value=env_config.get('api_base', ''),
            help="Custom API endpoint (optional)"
        )
    
    sandbox_endpoint = st.text_input(
        "Sandbox Fusion Endpoint",
        value=env_config.get('sandbox_fusion_endpoint', ''),
        help="Python code execution sandbox endpoint"
    )
    
    # Save environment configuration
    if st.button("💾 Save Environment Config"):
        new_env_config = {
            'serper_key_id': serper_key,
            'jina_api_keys': jina_key,
            'dashscope_api_key': dashscope_key,
            'api_key': api_key,
            'api_base': api_base,
            'sandbox_fusion_endpoint': sandbox_endpoint
        }
        
        config_manager.save_env_config(new_env_config)
        st.success("Environment configuration saved!")


def render_tools_config():
    """Render tools configuration section"""
    config_manager = st.session_state.config_manager
    tool_descriptions = config_manager.get_tool_descriptions()
    
    st.subheader("Available Tools")
    
    enabled_tools = []
    
    for tool_name, description in tool_descriptions.items():
        enabled = st.checkbox(
            tool_name.title(),
            value=True,
            help=description
        )
        if enabled:
            enabled_tools.append(tool_name)
    
    st.session_state.enabled_tools = enabled_tools
    
    if enabled_tools:
        st.success(f"✅ {len(enabled_tools)} tools enabled")
    else:
        st.warning("⚠️ No tools enabled - tasks may not work properly")


def render_task_controls():
    """Render task control buttons"""
    task_manager = st.session_state.task_manager
    
    # Quick start button
    if st.button("🚀 Quick Start", type="primary"):
        # Use sample questions for quick start
        config_manager = st.session_state.config_manager
        sample_questions = config_manager.get_sample_questions()
        
        # Create task with current configuration
        task_config = config_manager.create_task_config(
            st.session_state.get('model_config', {}),
            sample_questions
        )
        
        task_id = task_manager.create_task(task_config)
        
        if task_manager.start_task(task_id):
            st.session_state.current_task = task_manager.get_task(task_id)
            st.success(f"✅ Quick start task created: {task_id[:8]}")
            st.rerun()
        else:
            st.error("❌ Failed to start task")
    
    st.divider()
    
    # Current task controls
    current_task = st.session_state.current_task
    if current_task:
        st.subheader(f"Current Task: {current_task['id'][:8]}")
        
        status = current_task['status']
        if status == 'running':
            st.progress(current_task.get('progress', 0) / 100)
            st.caption(f"Progress: {current_task.get('progress', 0)}%")
            
            if st.button("⏹️ Cancel Task", type="secondary"):
                if task_manager.cancel_task(current_task['id']):
                    st.success("Task cancelled")
                    st.rerun()
        
        elif status == 'completed':
            st.success("✅ Task completed")
            
            if st.button("📥 Download Results"):
                markdown_content = task_manager.export_results_as_markdown(current_task['id'])
                if markdown_content:
                    st.download_button(
                        label="Download Markdown",
                        data=markdown_content,
                        file_name=f"research_results_{current_task['id'][:8]}.md",
                        mime="text/markdown"
                    )
        
        elif status == 'error':
            st.error(f"❌ Task failed: {current_task.get('error', 'Unknown error')}")
        
        # Clear current task
        if st.button("🗑️ Clear Task"):
            st.session_state.current_task = None
            st.rerun()