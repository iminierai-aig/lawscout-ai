#!/bin/bash
# Start LawScout AI Backend (FastAPI)

set -e

echo "🚀 Starting LawScout AI Backend..."
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: backend/main.py not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check for virtual environment
if [ -d "backend/venv" ]; then
    echo "📦 Activating virtual environment..."
    source backend/venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
    echo "   Consider creating one: python -m venv backend/venv"
fi

# Check for .env file
if [ ! -f ".env" ] && [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: No .env file found"
    echo "   Create .env file with:"
    echo "   QDRANT_URL=your_url"
    echo "   QDRANT_API_KEY=your_key"
    echo "   GEMINI_API_KEY=your_key"
    echo ""
fi

# Change to backend directory
cd backend

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Check for PyTorch
if ! python -c "import torch" 2>/dev/null; then
    echo "📥 Installing PyTorch CPU..."
    pip install torch==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu
    echo ""
fi

# Check for numpy (required for sentence-transformers and hybrid search)
# Must be <2.0 for PyTorch compatibility
NUMPY_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "")
if [ -z "$NUMPY_VERSION" ]; then
    echo "📥 Installing numpy..."
    pip install "numpy>=1.24.0,<2.0"
    echo ""
else
    # Check if numpy version starts with "2." (simple check)
    if [[ "$NUMPY_VERSION" == 2.* ]]; then
        echo "⚠️  NumPy 2.x detected (incompatible with PyTorch)"
        echo "📥 Downgrading to NumPy <2.0..."
        pip install "numpy>=1.24.0,<2.0" --force-reinstall
        echo ""
    fi
fi

# Start the server
echo "✅ Starting FastAPI server on http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

