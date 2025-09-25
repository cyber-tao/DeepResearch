#!/bin/bash
# DeepResearch WebUI Quick Launch Script

echo "🔍 DeepResearch WebUI Launcher"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "webui/app.py" ]; then
    echo "❌ Error: Please run this script from the DeepResearch root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: webui/app.py"
    exit 1
fi

# Check Python and dependencies
echo "🐍 Checking Python environment..."
python3 --version

if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing Streamlit..."
    pip install streamlit
fi

echo "✅ Environment ready!"
echo ""

# Set environment variables for better display
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_THEME_BASE=light

echo "🚀 Starting DeepResearch WebUI..."
echo "📱 Open your browser to: http://localhost:8501"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Launch WebUI
cd webui
python3 -m streamlit run app.py \
    --server.port 8501 \
    --server.headless true \
    --theme.base light \
    --server.address 0.0.0.0