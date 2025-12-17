#!/bin/bash
# Quick script to check backend logs and performance

echo "📊 Backend Performance Check"
echo "============================"
echo ""

# Check if backend is running
if ! pgrep -f "uvicorn main:app" > /dev/null; then
    echo "❌ Backend is not running"
    echo "   Start it with: ./scripts/start-backend.sh"
    exit 1
fi

echo "✅ Backend is running"
echo ""

# Check health endpoint
echo "🔍 Checking health endpoint..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "❌ Cannot reach backend"
fi

echo ""
echo "📝 To view real-time logs:"
echo "   1. Find the terminal where backend is running"
echo "   2. Look for lines with:"
echo "      - ⏱️  Search completed in X.XXs"
echo "      - ⏱️  Answer generation completed in X.XXs"
echo "      - ⏱️  Total pipeline time: X.XXs"
echo "   3. Or check API route logs:"
echo "      - Search completed: X sources found | Total time: X.XXs | ..."
echo ""
echo "💡 Tip: Make a test search request and watch the terminal output"

