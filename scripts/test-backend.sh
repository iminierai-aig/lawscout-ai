#!/bin/bash
# Test LawScout AI Backend

set -e

echo "🧪 Testing LawScout AI Backend..."
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo "1️⃣  Testing Health Endpoint..."
response=$(curl -s "$BASE_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo "   ✅ Health check passed"
    echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
else
    echo "   ❌ Health check failed"
    echo "$response"
    exit 1
fi
echo ""

# Test 2: API Docs
echo "2️⃣  Checking API Documentation..."
if curl -s "$BASE_URL/docs" | grep -q "FastAPI"; then
    echo "   ✅ API docs available at $BASE_URL/docs"
else
    echo "   ⚠️  API docs not accessible"
fi
echo ""

# Test 3: Search Endpoint
echo "3️⃣  Testing Search Endpoint..."
response=$(curl -s -X POST "$BASE_URL/api/v1/search" \
    -H "Content-Type: application/json" \
    -d '{
        "query": "What is breach of contract?",
        "collection": "both",
        "limit": 3
    }')

if echo "$response" | grep -q "sources"; then
    echo "   ✅ Search endpoint working"
    echo "$response" | python -m json.tool 2>/dev/null | head -20 || echo "$response" | head -20
else
    echo "   ❌ Search endpoint failed"
    echo "$response"
    exit 1
fi
echo ""

echo "✅ All backend tests passed!"
echo ""
echo "Backend is ready for frontend integration."

