#!/bin/bash
# Setup Local Development Environment

set -e

echo "🔧 Setting up LawScout AI Local Development Environment..."
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Backend Port (optional)
PORT=8000
EOF
    echo "✅ Created .env file"
    echo "   ⚠️  Please edit .env and add your API keys!"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Check for frontend .env.local
if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend/.env.local..."
    mkdir -p frontend
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ Created frontend/.env.local"
    echo ""
else
    echo "✅ frontend/.env.local already exists"
    echo ""
fi

# Setup backend virtual environment
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating backend virtual environment..."
    cd backend
    python -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    cd ..
else
    echo "✅ Backend virtual environment already exists"
    echo ""
fi

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install Python with pip."
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

# Install PyTorch CPU if not already installed
if ! python -c "import torch" 2>/dev/null; then
    echo "📥 Installing PyTorch CPU..."
    pip install torch==2.2.0+cpu --index-url https://download.pytorch.org/whl/cpu
fi

cd ..
echo "✅ Backend dependencies installed"
echo ""

# Setup frontend
echo "📥 Installing frontend dependencies..."
cd frontend

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js and npm."
    exit 1
fi

npm install
cd ..
echo "✅ Frontend dependencies installed"
echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x scripts/*.sh
echo "✅ Scripts are executable"
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file and add your API keys"
echo "  2. Start backend: ./scripts/start-backend.sh"
echo "  3. Start frontend: ./scripts/start-frontend.sh"
echo "  4. Test integration: ./scripts/test-integration.sh"
echo ""

