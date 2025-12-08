#!/bin/bash
# Fix NumPy version incompatibility (downgrade from 2.x to 1.x)

set -e

echo "🔧 Fixing NumPy version incompatibility..."
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

# Check current numpy version
CURRENT_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not installed")
echo "Current NumPy version: $CURRENT_VERSION"

# Check if numpy 2.x is installed (simple check: version starts with "2.")
if [ "$CURRENT_VERSION" = "not installed" ]; then
    echo "📥 Installing numpy..."
    pip install "numpy>=1.24.0,<2.0"
    echo ""
elif [[ "$CURRENT_VERSION" == 2.* ]]; then
    echo "⚠️  NumPy 2.x detected (incompatible with PyTorch)"
    echo "📥 Downgrading to NumPy <2.0..."
    pip install "numpy>=1.24.0,<2.0" --force-reinstall
    echo ""
else
    echo "✅ NumPy version is compatible (<2.0)"
    echo ""
fi

# Verify installation
NEW_VERSION=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null)
if [[ "$NEW_VERSION" == 2.* ]]; then
    echo "❌ Failed to fix NumPy version (still 2.x)"
    exit 1
else
    echo "✅ NumPy $NEW_VERSION installed successfully!"
    echo ""
    echo "You can now restart the backend:"
    echo "   ./scripts/start-backend.sh"
fi

