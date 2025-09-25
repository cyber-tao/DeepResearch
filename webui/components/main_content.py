"""
Main content area components
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any


def render_main_content():
    """Render the main content area"""
    
    # Main tabs
    input_tab, results_tab, history_tab = st.tabs(["📝 Input & Setup", "📊 Results", "📋 Task History"])
    
    with input_tab:
        render_input_section()
    
    with results_tab:
        render_results_section()
    
    with history_tab:
        render_history_section()


def render_input_section():
    """Render the input and setup section"""
    
    st.header("Research Task Setup")
    
    # Task input methods
    input_method = st.radio(
        "How would you like to provide research questions?",
        ["Manual Input", "Upload File", "Sample Questions"],
        horizontal=True
    )
    
    questions = []
    
    if input_method == "Manual Input":
        questions = render_manual_input()
    
    elif input_method == "Upload File":
        questions = render_file_upload()
    
    elif input_method == "Sample Questions":
        questions = render_sample_questions()
    
    # Task validation and creation
    if questions:
        render_task_creation(questions)


def render_manual_input() -> List[Dict[str, str]]:
    """Render manual input interface"""
    
    st.subheader("Manual Question Input")
    
    # Initialize session state for questions
    if 'manual_questions' not in st.session_state:
        st.session_state.manual_questions = [{'question': '', 'answer': ''}]
    
    questions = st.session_state.manual_questions
    
    # Display existing questions
    for i, q in enumerate(questions):
        with st.expander(f"Question {i+1}", expanded=(i == len(questions) - 1)):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                question_text = st.text_area(
                    "Research Question",
                    value=q['question'],
                    key=f"question_{i}",
                    help="Enter the research question you want to investigate",
                    placeholder="e.g., What are the latest developments in AI?"
                )
                
                answer_text = st.text_area(
                    "Reference Answer (Optional)",
                    value=q['answer'],
                    key=f"answer_{i}",
                    help="Optional reference answer for evaluation",
                    placeholder="Leave empty if not available"
                )
            
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button(f"🗑️", key=f"delete_{i}", help="Delete question"):
                    if len(questions) > 1:
                        questions.pop(i)
                        st.rerun()
            
            # Update the question in session state
            questions[i]['question'] = question_text
            questions[i]['answer'] = answer_text
    
    # Add/remove questions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Question"):
            st.session_state.manual_questions.append({'question': '', 'answer': ''})
            st.rerun()
    
    with col2:
        if st.button("🧹 Clear All") and len(questions) > 0:
            st.session_state.manual_questions = [{'question': '', 'answer': ''}]
            st.rerun()
    
    # Filter out empty questions
    valid_questions = [q for q in questions if q['question'].strip()]
    
    if valid_questions:
        st.info(f"📊 {len(valid_questions)} question(s) ready")
    
    return valid_questions


def render_file_upload() -> List[Dict[str, str]]:
    """Render file upload interface"""
    
    st.subheader("Upload Research Questions")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['json', 'jsonl', 'txt', 'csv'],
        help="Upload JSON, JSONL, TXT, or CSV file with research questions"
    )
    
    questions = []
    
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.read()
            
            if uploaded_file.name.endswith('.json'):
                data = json.loads(file_content.decode('utf-8'))
                if isinstance(data, list):
                    questions = [
                        {
                            'question': item.get('question', ''),
                            'answer': item.get('answer', '')
                        }
                        for item in data if isinstance(item, dict) and item.get('question')
                    ]
            
            elif uploaded_file.name.endswith('.jsonl'):
                lines = file_content.decode('utf-8').strip().split('\n')
                for line in lines:
                    if line.strip():
                        item = json.loads(line)
                        if item.get('question'):
                            questions.append({
                                'question': item['question'],
                                'answer': item.get('answer', '')
                            })
            
            elif uploaded_file.name.endswith('.txt'):
                lines = file_content.decode('utf-8').strip().split('\n')
                questions = [
                    {'question': line.strip(), 'answer': ''}
                    for line in lines if line.strip()
                ]
            
            elif uploaded_file.name.endswith('.csv'):
                # Try to parse CSV
                import io
                df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
                
                # Look for question column
                question_col = None
                answer_col = None
                
                for col in df.columns:
                    if 'question' in col.lower():
                        question_col = col
                    elif 'answer' in col.lower():
                        answer_col = col
                
                if question_col:
                    questions = []
                    for _, row in df.iterrows():
                        question = str(row[question_col]).strip()
                        answer = str(row[answer_col]).strip() if answer_col else ''
                        if question and question != 'nan':
                            questions.append({
                                'question': question,
                                'answer': answer if answer != 'nan' else ''
                            })
            
            if questions:
                st.success(f"✅ Loaded {len(questions)} question(s)")
                
                # Preview
                with st.expander("Preview Questions"):
                    for i, q in enumerate(questions[:5]):  # Show first 5
                        st.write(f"**Q{i+1}:** {q['question']}")
                        if q['answer']:
                            st.write(f"**A{i+1}:** {q['answer'][:100]}...")
                        st.divider()
                    
                    if len(questions) > 5:
                        st.write(f"... and {len(questions) - 5} more questions")
            else:
                st.error("❌ No valid questions found in file")
        
        except Exception as e:
            st.error(f"❌ Error parsing file: {str(e)}")
    
    return questions


def render_sample_questions() -> List[Dict[str, str]]:
    """Render sample questions interface"""
    
    st.subheader("Sample Research Questions")
    
    config_manager = st.session_state.config_manager
    sample_questions = config_manager.get_sample_questions()
    
    st.info("🌟 These are example research questions to help you get started")
    
    # Display sample questions
    for i, q in enumerate(sample_questions):
        with st.expander(f"Sample Question {i+1}", expanded=True):
            st.write(f"**Question:** {q['question']}")
            if q['answer']:
                st.write(f"**Reference Answer:** {q['answer']}")
    
    return sample_questions


def render_task_creation(questions: List[Dict[str, str]]):
    """Render task creation section"""
    
    st.divider()
    st.subheader("Create Research Task")
    
    # Task configuration summary
    with st.expander("Configuration Summary", expanded=False):
        model_config = st.session_state.get('model_config', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Model Settings:**")
            st.write(f"- Model: {model_config.get('model', 'Not set')}")
            st.write(f"- Temperature: {model_config.get('temperature', 'Not set')}")
            st.write(f"- Top-p: {model_config.get('top_p', 'Not set')}")
        
        with col2:
            st.write("**Execution Settings:**")
            st.write(f"- Max Workers: {model_config.get('max_workers', 'Not set')}")
            st.write(f"- Rollouts: {model_config.get('rollout_count', 'Not set')}")
            st.write(f"- Questions: {len(questions)}")
    
    # Validation
    config_manager = st.session_state.config_manager
    model_config = st.session_state.get('model_config', {})
    
    # Combine configuration with environment settings
    full_config = config_manager.create_task_config(model_config, questions)
    validation_errors = config_manager.validate_config(full_config)
    
    if validation_errors:
        st.error("❌ Configuration Issues:")
        for error in validation_errors:
            st.write(f"- {error}")
        return
    
    # Task creation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Start Research Task", type="primary", use_container_width=True):
            task_manager = st.session_state.task_manager
            
            # Create and start task
            task_id = task_manager.create_task(full_config)
            
            if task_manager.start_task(task_id):
                st.session_state.current_task = task_manager.get_task(task_id)
                st.success(f"✅ Task started: {task_id[:8]}")
                st.rerun()
            else:
                st.error("❌ Failed to start task")
    
    with col2:
        if st.button("💾 Save Configuration", use_container_width=True):
            # Save current configuration for later use
            config_file = f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            st.download_button(
                label="Download Config",
                data=json.dumps(full_config, indent=2),
                file_name=config_file,
                mime="application/json"
            )


def render_results_section():
    """Render the results section"""
    
    current_task = st.session_state.current_task
    
    if not current_task:
        st.info("🔍 No active task. Create a new research task to see results here.")
        return
    
    st.header(f"Results - Task {current_task['id'][:8]}")
    
    # Task status card
    status = current_task['status']
    status_colors = {
        'created': '🔵',
        'running': '🟡',
        'completed': '🟢',
        'error': '🔴',
        'cancelled': '⚫'
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Status", f"{status_colors.get(status, '⚪')} {status.title()}")
    
    with col2:
        progress = current_task.get('progress', 0)
        st.metric("Progress", f"{progress}%")
    
    with col3:
        results_count = len(current_task.get('results', []))
        st.metric("Results", results_count)
    
    with col4:
        config = current_task.get('config', {})
        total_questions = len(config.get('questions', []))
        st.metric("Questions", total_questions)
    
    # Progress bar
    if status == 'running':
        st.progress(progress / 100)
        st.caption(f"Processing question {results_count + 1} of {total_questions}")
    
    # Results display
    results = current_task.get('results', [])
    
    if results:
        st.subheader("Research Results")
        
        for i, result in enumerate(results):
            with st.expander(f"Result {i+1}: {result['question'][:50]}...", expanded=(i == 0)):
                
                # Question
                st.write("**🤔 Question:**")
                st.write(result['question'])
                
                # Answer
                st.write("**🤖 Research Result:**")
                st.markdown(result['prediction'])
                
                # Reference answer (if available)
                if result.get('answer'):
                    st.write("**📚 Reference Answer:**")
                    st.info(result['answer'])
                
                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"Completed: {result['timestamp']}")
                
                with col2:
                    if st.button(f"📋 Copy Result {i+1}", key=f"copy_{i}"):
                        st.code(result['prediction'])
    
    # Execution logs
    logs = current_task.get('logs', [])
    if logs:
        with st.expander("📜 Execution Logs"):
            for log in logs[-20:]:  # Show last 20 logs
                timestamp = log['timestamp'].split('T')[1].split('.')[0]  # Extract time
                st.text(f"[{timestamp}] {log['message']}")
    
    # Export options
    if status == 'completed' and results:
        st.subheader("📤 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Markdown export
            task_manager = st.session_state.task_manager
            markdown_content = task_manager.export_results_as_markdown(current_task['id'])
            
            if markdown_content:
                st.download_button(
                    label="📝 Download as Markdown",
                    data=markdown_content,
                    file_name=f"research_results_{current_task['id'][:8]}.md",
                    mime="text/markdown",
                    type="primary"
                )
        
        with col2:
            # JSON export
            json_content = json.dumps(current_task, indent=2, ensure_ascii=False)
            st.download_button(
                label="📊 Download as JSON",
                data=json_content,
                file_name=f"research_results_{current_task['id'][:8]}.json",
                mime="application/json"
            )


def render_history_section():
    """Render the task history section"""
    
    st.header("Task History")
    
    task_manager = st.session_state.task_manager
    all_tasks = task_manager.get_all_tasks()
    
    if not all_tasks:
        st.info("📊 No tasks found. Create your first research task to see history here.")
        return
    
    # Sort tasks by creation time (newest first)
    all_tasks.sort(key=lambda x: x['created_at'], reverse=True)
    
    for task in all_tasks:
        with st.expander(
            f"Task {task['id'][:8]} - {task['status'].title()} - {task['created_at'][:10]}",
            expanded=False
        ):
            
            # Task metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Status:** {task['status'].title()}")
                st.write(f"**Created:** {task['created_at'][:19].replace('T', ' ')}")
            
            with col2:
                results_count = len(task.get('results', []))
                questions_count = len(task.get('config', {}).get('questions', []))
                st.write(f"**Results:** {results_count}/{questions_count}")
                if task.get('started_at'):
                    st.write(f"**Started:** {task['started_at'][:19].replace('T', ' ')}")
            
            with col3:
                if task.get('completed_at'):
                    st.write(f"**Completed:** {task['completed_at'][:19].replace('T', ' ')}")
                if task.get('error'):
                    st.error(f"**Error:** {task['error'][:50]}...")
            
            # Configuration summary
            config = task.get('config', {})
            st.write(f"**Model:** {config.get('model', 'Unknown')}")
            
            # Actions
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button(f"👁️ View", key=f"view_{task['id']}"):
                    st.session_state.current_task = task
                    st.rerun()
            
            with col2:
                if task['status'] == 'completed':
                    markdown_content = task_manager.export_results_as_markdown(task['id'])
                    if markdown_content:
                        st.download_button(
                            label="📝 Export",
                            data=markdown_content,
                            file_name=f"results_{task['id'][:8]}.md",
                            mime="text/markdown",
                            key=f"export_{task['id']}"
                        )
            
            with col3:
                json_content = json.dumps(task, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📊 JSON",
                    data=json_content,
                    file_name=f"task_{task['id'][:8]}.json",
                    mime="application/json",
                    key=f"json_{task['id']}"
                )
            
            with col4:
                if st.button(f"🗑️ Delete", key=f"delete_{task['id']}", type="secondary"):
                    if task_manager.delete_task(task['id']):
                        st.success("Task deleted")
                        st.rerun()