#!/bin/bash
# Pre-Deployment Test Script for LawScout AI v2.0
# Run this before deploying to production

set -e  # Exit on any error

echo "======================================"
echo "🧪 LawScout AI v2.0 Pre-Deployment Tests"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}: $2"
        ((FAILED++))
    fi
}

echo "📋 Test 1: Check Python dependencies"
echo "--------------------------------------"
python3 -c "import rank_bm25" 2>/dev/null
test_result $? "rank-bm25 installed"

python3 -c "import transformers" 2>/dev/null
test_result $? "transformers installed"

python3 -c "import sentence_transformers" 2>/dev/null
test_result $? "sentence-transformers installed"

python3 -c "import qdrant_client" 2>/dev/null
test_result $? "qdrant-client installed"

python3 -c "import google.generativeai" 2>/dev/null
test_result $? "google-generativeai installed"

echo ""
echo "📋 Test 2: Check environment variables"
echo "--------------------------------------"
if [ -f ".env" ]; then
    source .env
    [ ! -z "$QDRANT_URL" ]
    test_result $? "QDRANT_URL set"
    
    [ ! -z "$QDRANT_API_KEY" ]
    test_result $? "QDRANT_API_KEY set"
    
    [ ! -z "$GEMINI_API_KEY" ]
    test_result $? "GEMINI_API_KEY set"
else
    echo -e "${YELLOW}⚠️  WARN${NC}: .env file not found (OK if using env vars)"
fi

echo ""
echo "📋 Test 3: Check critical files exist"
echo "--------------------------------------"
[ -f "rag_system/rag_engine.py" ]
test_result $? "rag_engine.py exists"

[ -f "rag_system/hybrid_search.py" ]
test_result $? "hybrid_search.py exists"

[ -f "rag_system/citation_utils.py" ]
test_result $? "citation_utils.py exists"

[ -f "web_app/app.py" ]
test_result $? "app.py exists"

[ -f "Dockerfile" ]
test_result $? "Dockerfile exists"

[ -f "requirements.txt" ]
test_result $? "requirements.txt exists"

echo ""
echo "📋 Test 4: Verify Dockerfile has new dependencies"
echo "--------------------------------------"
grep -q "rank-bm25" Dockerfile
test_result $? "Dockerfile includes rank-bm25"

grep -q "transformers" Dockerfile
test_result $? "Dockerfile includes transformers"

grep -q "sentence-transformers==3.3.1" Dockerfile
test_result $? "Dockerfile has updated sentence-transformers"

grep -q "google-generativeai==0.8.3" Dockerfile
test_result $? "Dockerfile has updated google-generativeai"

echo ""
echo "📋 Test 5: Check git status"
echo "--------------------------------------"
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Check if there are uncommitted changes
    if [[ -z $(git status -s) ]]; then
        test_result 0 "No uncommitted changes"
    else
        test_result 1 "Uncommitted changes exist - commit before deploying"
        echo "   Run: git status to see changes"
    fi
else
    echo -e "${YELLOW}⚠️  WARN${NC}: Not a git repository"
fi

echo ""
echo "📋 Test 6: Test Gemini API access"
echo "--------------------------------------"
if [ ! -z "$GEMINI_API_KEY" ]; then
    python3 -c "
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=key)

try:
    models = genai.list_models()
    found_2_5 = False
    for m in models:
        if 'gemini-2.5-flash' in m.name:
            found_2_5 = True
            break
    
    if found_2_5:
        print('✅ Gemini 2.5 Flash available')
        exit(0)
    else:
        print('⚠️  Gemini 2.5 Flash not found')
        exit(1)
except Exception as e:
    print(f'❌ API Error: {e}')
    exit(1)
" 2>&1
    test_result $? "Gemini 2.5 Flash accessible"
else
    echo -e "${YELLOW}⚠️  SKIP${NC}: GEMINI_API_KEY not set"
fi

echo ""
echo "======================================"
echo "📊 Test Summary"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "Failed: $FAILED"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git diff"
    echo "  2. Commit: git add . && git commit -m 'feat: v2.0'"
    echo "  3. Tag: git tag v2.0.0"
    echo "  4. Push: git push origin master --tags"
    echo "  5. Build: docker build -t lawscout-ai:latest ."
    echo "  6. Deploy: Follow DEPLOY_V2.md"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Fix issues before deploying.${NC}"
    echo ""
    exit 1
fi

