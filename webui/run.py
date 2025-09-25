#!/usr/bin/env python3
"""
DeepResearch WebUI Runner Script
Launch the WebUI application
"""

import sys
import os
import subprocess
from pathlib import Path

# Add parent directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Launch the WebUI application"""
    
    # Check if streamlit is available
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} found")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} installed")
    
    # Set environment variables for better display
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_THEME_BASE'] = 'light'
    
    # Get the app path
    app_path = Path(__file__).parent / "app.py"
    
    print(f"🚀 Starting DeepResearch WebUI...")
    print(f"📁 App path: {app_path}")
    print(f"🌐 Open your browser to http://localhost:8501")
    print(f"⏹️  Press Ctrl+C to stop the server")
    
    # Launch streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_path),
            "--server.port", "8501",
            "--server.headless", "true",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 WebUI stopped by user")
    except Exception as e:
        print(f"❌ Error starting WebUI: {e}")

if __name__ == "__main__":
    main()