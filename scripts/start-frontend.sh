#!/bin/bash
# Start LawScout AI Frontend (Next.js)

set -e

echo "🚀 Starting LawScout AI Frontend..."
echo ""

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: frontend/package.json not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Change to frontend directory
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
    echo ""
fi

# Check for .env.local
if [ ! -f ".env.local" ]; then
    echo "⚠️  No .env.local found. Creating default..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    echo "✅ Created .env.local"
    echo ""
fi

# Start the dev server
echo "✅ Starting Next.js dev server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

npm run dev

