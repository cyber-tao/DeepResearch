# DeepResearch WebUI

A comprehensive web interface for configuring, running, and monitoring DeepResearch tasks with an intuitive user experience.

## Features

🚀 **Easy Task Configuration**
- Model parameter adjustment (temperature, top-p, presence penalty)
- API key management with secure storage
- Tool selection and configuration
- Multi-format question input (manual, file upload, samples)

📊 **Real-time Monitoring** 
- Live progress tracking during task execution
- Detailed execution logs and status updates
- Task queue management with cancel functionality
- Rich results display with formatting

📝 **Results Management**
- Export results as Markdown files
- JSON export for programmatic access  
- Task history with search and filtering
- Comparison between multiple task runs

✨ **Modern UI/UX**
- Clean, responsive design with custom styling
- Tabbed interface for organized workflow
- Real-time updates without page refresh
- Mobile-friendly responsive layout

## Quick Start

### 1. Launch the WebUI

```bash
# From the DeepResearch root directory
cd webui
python run.py
```

The WebUI will start at `http://localhost:8501`

### 2. Configure Environment

1. Go to the **Environment** tab in the sidebar
2. Enter your API keys:
   - **Serper API Key**: For web search functionality
   - **Jina API Key**: For web page reading  
   - **DashScope API Key**: For file parsing and models
   - **OpenAI API Key**: Alternative model access
3. Click "💾 Save Environment Config"

### 3. Set Up Your Research Task

1. Go to the **Input & Setup** tab
2. Choose how to input your research questions:
   - **Manual Input**: Type questions directly
   - **Upload File**: Upload JSON, JSONL, TXT, or CSV files
   - **Sample Questions**: Use provided examples
3. Configure model parameters in the sidebar
4. Click "🚀 Start Research Task"

### 4. Monitor Progress

- Watch real-time progress in the **Results** tab
- View detailed execution logs
- Cancel running tasks if needed

### 5. Export Results

- Download results as Markdown files
- Export raw data as JSON
- View task history for comparison

## File Upload Formats

### JSON Format
```json
[
  {
    "question": "What are the latest AI developments?",
    "answer": "Optional reference answer"
  }
]
```

### JSONL Format
```jsonl
{"question": "Question 1", "answer": "Optional answer"}
{"question": "Question 2", "answer": "Optional answer"}
```

### CSV Format
```csv
question,answer
"What is quantum computing?","Optional reference answer"
"How do neural networks work?",""
```

### TXT Format
```
What are the latest AI developments?
How do neural networks work?
What is quantum computing?
```

## Configuration

### Model Parameters

- **Temperature** (0.0-2.0): Controls response randomness
- **Top-p** (0.0-1.0): Nucleus sampling parameter  
- **Presence Penalty** (0.0-2.0): Reduces repetition
- **Max Workers**: Concurrent execution threads
- **Rollout Count**: Number of attempts per question

### Available Tools

- **🔍 Search**: Web search via Serper API
- **🌐 Visit**: Web page analysis via Jina API  
- **📚 Scholar**: Academic paper search
- **📄 File Parser**: Document parsing (PDF, Office, etc.)
- **🐍 Python**: Code execution in sandboxed environment

## API Keys Required

| Service | Purpose | Get Key From |
|---------|---------|-------------|
| Serper | Web search, Google Scholar | [serper.dev](https://serper.dev/) |
| Jina | Web page reading | [jina.ai](https://jina.ai/) |
| DashScope | File parsing, Qwen models | [dashscope.aliyun.com](https://dashscope.aliyun.com/) |
| OpenAI | GPT models (optional) | [platform.openai.com](https://platform.openai.com/) |
| SandboxFusion | Python execution (optional) | [github.com/bytedance/SandboxFusion](https://github.com/bytedance/SandboxFusion) |

## Architecture

```
webui/
├── app.py              # Main Streamlit application
├── run.py              # Launch script
├── components/         # UI components
│   ├── sidebar.py      # Configuration sidebar
│   ├── main_content.py # Main content area
│   └── task_status.py  # Status widgets
└── utils/              # Backend utilities
    ├── config_manager.py # Configuration management
    └── task_manager.py   # Task execution and monitoring
```

## Troubleshooting

### Common Issues

**Import Errors**: Make sure you're running from the correct directory and all dependencies are installed.

**API Key Errors**: Verify your API keys are correctly entered and have sufficient credits/permissions.

**Task Stuck**: Check the execution logs for specific errors. Cancel and restart if needed.

**File Upload Issues**: Ensure your file format matches the expected structure shown above.

### Getting Help

1. Check the execution logs in the WebUI
2. Review the configuration summary before starting tasks
3. Try the sample questions first to verify setup
4. Open an issue on GitHub if problems persist

## Development

### Adding New Components

1. Create component in `webui/components/`
2. Import in `webui/components/__init__.py`
3. Use in `app.py` or other components

### Extending Task Manager

1. Add methods to `TaskManager` class
2. Update UI components to use new functionality
3. Test with various configurations

### Custom Styling

Modify the CSS in `app.py` to customize appearance:

```python
st.markdown("""
<style>
/* Your custom styles here */
</style>
""", unsafe_allow_html=True)
```