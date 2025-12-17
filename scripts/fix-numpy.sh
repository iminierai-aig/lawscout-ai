#!/bin/bash
# Quick fix for numpy missing error

set -e

echo "🔧 Fixing numpy installation..."
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
fi

# Install numpy (must be <2.0 for PyTorch compatibility)
echo "📥 Installing numpy (version <2.0 for PyTorch compatibility)..."
pip install "numpy>=1.24.0,<2.0"

# Verify installation
if python -c "import numpy; print(f'✅ numpy {numpy.__version__} installed')" 2>/dev/null; then
    echo ""
    echo "✅ Numpy installed successfully!"
    echo ""
    echo "You can now restart the backend:"
    echo "   ./scripts/start-backend.sh"
else
    echo "❌ Failed to install numpy"
    exit 1
fi

