"""
Task status component for real-time monitoring
"""

import streamlit as st
from typing import Dict, Any


def render_task_status_widget(task: Dict[str, Any]):
    """Render a compact task status widget"""
    
    if not task:
        return
    
    status = task['status']
    progress = task.get('progress', 0)
    
    # Status indicator
    status_colors = {
        'created': '🔵',
        'running': '🟡', 
        'completed': '🟢',
        'error': '🔴',
        'cancelled': '⚫'
    }
    
    status_icon = status_colors.get(status, '⚪')
    
    # Progress bar for running tasks
    if status == 'running':
        st.progress(progress / 100)
        st.caption(f"{status_icon} {status.title()} - {progress}%")
    else:
        st.caption(f"{status_icon} {status.title()}")


def render_task_metrics(task: Dict[str, Any]):
    """Render task metrics in a compact format"""
    
    if not task:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        results_count = len(task.get('results', []))
        st.metric("Results", results_count)
    
    with col2:
        config = task.get('config', {})
        total_questions = len(config.get('questions', []))
        st.metric("Questions", total_questions)
    
    with col3:
        if task.get('started_at'):
            duration = _calculate_duration(task)
            st.metric("Duration", duration)


def _calculate_duration(task: Dict[str, Any]) -> str:
    """Calculate task duration"""
    from datetime import datetime
    
    if not task.get('started_at'):
        return "Not started"
    
    start_time = datetime.fromisoformat(task['started_at'])
    
    if task.get('completed_at'):
        end_time = datetime.fromisoformat(task['completed_at'])
    else:
        end_time = datetime.now()
    
    duration = end_time - start_time
    
    # Format duration nicely
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"