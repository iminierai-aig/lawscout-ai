#!/bin/bash
# Test Full Integration (Backend + Frontend)

set -e

echo "🧪 Testing LawScout AI Integration..."
echo ""

# Check if backend is running
echo "1️⃣  Checking Backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not running"
    echo "   Start it with: ./scripts/start-backend.sh"
    exit 1
fi
echo ""

# Check if frontend is running
echo "2️⃣  Checking Frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is not running"
    echo "   Start it with: ./scripts/start-frontend.sh"
    exit 1
fi
echo ""

# Test API connection from frontend perspective
echo "3️⃣  Testing API Connection..."
response=$(curl -s -X POST "http://localhost:8000/api/v1/search" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "What is breach of contract?",
        "collection": "both",
        "limit": 5
    }')

if echo "$response" | grep -q "sources"; then
    echo "   ✅ API connection working"
    source_count=$(echo "$response" | python -c "import sys, json; print(len(json.load(sys.stdin)['sources']))" 2>/dev/null || echo "?")
    echo "   📊 Found $source_count sources"
else
    echo "   ❌ API connection failed"
    echo "$response"
    exit 1
fi
echo ""

# Test CORS
echo "4️⃣  Testing CORS..."
cors_headers=$(curl -s -I -X OPTIONS "http://localhost:8000/api/v1/search" \
    -H "Origin: http://localhost:3000" \
    -H "Access-Control-Request-Method: POST" | grep -i "access-control")

if [ -n "$cors_headers" ]; then
    echo "   ✅ CORS configured"
    echo "   $cors_headers"
else
    echo "   ⚠️  CORS headers not found (may still work)"
fi
echo ""

echo "✅ Integration tests passed!"
echo ""
echo "🌐 Open http://localhost:3000 in your browser to test the UI"
echo ""
echo "Test queries:"
echo "  - What is breach of contract?"
echo "  - Explain qualified immunity"
echo "  - What is the standard for summary judgment?"

