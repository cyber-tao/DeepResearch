"""
Task Manager - Handles research task execution, monitoring, and results
"""

import json
import os
import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import tempfile
import asyncio
from pathlib import Path

class TaskManager:
    """Manages research tasks execution and monitoring"""
    
    def __init__(self):
        self.tasks = {}
        self.results_dir = Path("webui_results")
        self.results_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
    
    def create_task(self, config: Dict[str, Any]) -> str:
        """Create a new research task"""
        task_id = str(uuid.uuid4())
        
        with self.lock:
            self.tasks[task_id] = {
                'id': task_id,
                'config': config,
                'status': 'created',
                'progress': 0,
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
                'results': [],
                'logs': [],
                'error': None
            }
        
        return task_id
    
    def start_task(self, task_id: str) -> bool:
        """Start executing a research task"""
        if task_id not in self.tasks:
            return False
        
        with self.lock:
            task = self.tasks[task_id]
            if task['status'] != 'created':
                return False
            
            task['status'] = 'running'
            task['started_at'] = datetime.now().isoformat()
        
        # Start task execution in background thread
        thread = threading.Thread(target=self._execute_task, args=(task_id,))
        thread.daemon = True
        thread.start()
        
        return True
    
    def _execute_task(self, task_id: str):
        """Execute the research task (runs in background thread)"""
        try:
            task = self.tasks[task_id]
            config = task['config']
            
            self._log(task_id, f"Starting task with config: {json.dumps(config, indent=2)}")
            
            # Import agent here to avoid circular imports
            import sys
            import os
            inference_path = os.path.join(os.path.dirname(__file__), '..', '..', 'inference')
            sys.path.append(inference_path)
            from react_agent import MultiTurnReactAgent
            
            # Prepare LLM configuration
            llm_cfg = {
                'model': config.get('model', 'qwen-plus'),
                'generate_cfg': {
                    'temperature': config.get('temperature', 0.6),
                    'top_p': config.get('top_p', 0.95),
                    'presence_penalty': config.get('presence_penalty', 1.1),
                    'max_input_tokens': config.get('max_input_tokens', 320000),
                    'max_retries': config.get('max_retries', 10)
                },
                'model_type': 'qwen_dashscope'
            }
            
            # Create agent
            agent = MultiTurnReactAgent(
                llm=llm_cfg,
                function_list=["search", "visit", "file_parser", "scholar", "python"]
            )
            
            # Process questions
            questions = config.get('questions', [])
            total_questions = len(questions)
            
            for i, question_data in enumerate(questions):
                if self.tasks[task_id]['status'] != 'running':
                    break  # Task was cancelled
                
                self._log(task_id, f"Processing question {i+1}/{total_questions}: {question_data.get('question', 'Unknown')}")
                
                # Update progress
                progress = int((i / total_questions) * 100)
                with self.lock:
                    self.tasks[task_id]['progress'] = progress
                
                # Prepare task data for agent
                item = {
                    'question': question_data.get('question', ''),
                    'answer': question_data.get('answer', '')
                }
                
                # Execute the research task
                result = agent._run({'item': item, 'planning_port': 6001}, config.get('model', 'qwen-plus'))
                
                # Store result
                result_data = {
                    'question': item['question'],
                    'answer': item['answer'],
                    'prediction': result[-1]['content'] if result and len(result) > 0 else 'No response',
                    'messages': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                with self.lock:
                    self.tasks[task_id]['results'].append(result_data)
            
            # Task completed successfully
            with self.lock:
                self.tasks[task_id]['status'] = 'completed'
                self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
                self.tasks[task_id]['progress'] = 100
            
            self._log(task_id, "Task completed successfully")
            
            # Save results to file
            self._save_results(task_id)
            
        except Exception as e:
            # Task failed
            error_msg = str(e)
            self._log(task_id, f"Task failed with error: {error_msg}")
            
            with self.lock:
                self.tasks[task_id]['status'] = 'error'
                self.tasks[task_id]['error'] = error_msg
                self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
    
    def _log(self, task_id: str, message: str):
        """Add a log entry to the task"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'message': message
        }
        
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]['logs'].append(log_entry)
    
    def _save_results(self, task_id: str):
        """Save task results to file"""
        task = self.tasks[task_id]
        results_file = self.results_dir / f"task_{task_id}.json"
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, indent=2, ensure_ascii=False)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id not in self.tasks:
            return False
        
        with self.lock:
            task = self.tasks[task_id]
            if task['status'] == 'running':
                task['status'] = 'cancelled'
                task['completed_at'] = datetime.now().isoformat()
                self._log(task_id, "Task cancelled by user")
                return True
        
        return False
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task information"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks"""
        with self.lock:
            return list(self.tasks.values())
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task and its results"""
        if task_id not in self.tasks:
            return False
        
        with self.lock:
            # Remove from memory
            del self.tasks[task_id]
            
            # Remove results file if it exists
            results_file = self.results_dir / f"task_{task_id}.json"
            if results_file.exists():
                results_file.unlink()
        
        return True
    
    def export_results_as_markdown(self, task_id: str) -> Optional[str]:
        """Export task results as markdown"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        markdown_content = []
        markdown_content.append(f"# DeepResearch Results - {task['id']}\n")
        markdown_content.append(f"**Created:** {task['created_at']}")
        markdown_content.append(f"**Status:** {task['status']}")
        markdown_content.append(f"**Duration:** {self._calculate_duration(task)}\n")
        
        if task.get('config'):
            markdown_content.append("## Configuration")
            markdown_content.append("```json")
            markdown_content.append(json.dumps(task['config'], indent=2))
            markdown_content.append("```\n")
        
        if task.get('results'):
            markdown_content.append("## Research Results\n")
            for i, result in enumerate(task['results'], 1):
                markdown_content.append(f"### Question {i}")
                markdown_content.append(f"**Q:** {result.get('question', 'N/A')}\n")
                markdown_content.append("**Research Result:**")
                markdown_content.append(f"{result.get('prediction', 'No response')}\n")
                
                if result.get('answer'):
                    markdown_content.append("**Reference Answer:**")
                    markdown_content.append(f"{result['answer']}\n")
                
                markdown_content.append("---\n")
        
        if task.get('logs'):
            markdown_content.append("## Execution Logs\n")
            markdown_content.append("```")
            for log in task['logs']:
                markdown_content.append(f"[{log['timestamp']}] {log['message']}")
            markdown_content.append("```\n")
        
        return '\n'.join(markdown_content)
    
    def _calculate_duration(self, task: Dict[str, Any]) -> str:
        """Calculate task duration"""
        if not task.get('started_at'):
            return "Not started"
        
        start_time = datetime.fromisoformat(task['started_at'])
        
        if task.get('completed_at'):
            end_time = datetime.fromisoformat(task['completed_at'])
        else:
            end_time = datetime.now()
        
        duration = end_time - start_time
        return str(duration).split('.')[0]  # Remove microseconds