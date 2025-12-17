#!/bin/bash
# Fix Frontend API URL - Rebuild with correct backend URL

set -e

echo "🔧 Fixing Frontend API URL Configuration"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Get backend URL
echo "📋 What is your backend URL on Render?"
echo "   Example: https://lawscout-backend-latest.onrender.com"
read -p "Backend URL: " BACKEND_URL

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}❌ Backend URL is required${NC}"
    exit 1
fi

# Remove trailing slash if present
BACKEND_URL="${BACKEND_URL%/}"

echo ""
echo "🔍 Verifying backend is accessible..."
if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Cannot reach backend at $BACKEND_URL/health${NC}"
    echo "   Continuing anyway (might be CORS or network issue)..."
fi
echo ""

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set${NC}"
    echo "   Set it with: export GITHUB_TOKEN=your_token"
    echo ""
    read -p "Continue without pushing to registry? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    PUSH_TO_REGISTRY=false
else
    PUSH_TO_REGISTRY=true
fi

# GitHub Container Registry
REGISTRY="ghcr.io"
ORG="iminierai-aig"
VERSION="v2.1.1"

# Login if pushing
if [ "$PUSH_TO_REGISTRY" = true ]; then
    echo "🔐 Logging in to GitHub Container Registry..."
    echo "$GITHUB_TOKEN" | docker login $REGISTRY -u "$(git config user.name)" --password-stdin || {
        echo -e "${RED}❌ Failed to login${NC}"
        exit 1
    }
    echo -e "${GREEN}✅ Logged in${NC}"
    echo ""
fi

# Build frontend with correct backend URL
echo "📦 Building Frontend with Backend URL: $BACKEND_URL"
cd frontend

# Clean up old local images
echo "   Cleaning up old local images..."
docker rmi $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION 2>/dev/null || true
docker rmi lawscout-frontend:$VERSION 2>/dev/null || true

echo "   Building Docker image..."
docker build \
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
    -t $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION . || {
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
}

echo "   Tagging as latest..."
docker tag $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION \
           $REGISTRY/$ORG/lawscout-ai-frontend:latest

if [ "$PUSH_TO_REGISTRY" = true ]; then
    echo "   Pushing to registry..."
    docker push $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION
    docker push $REGISTRY/$ORG/lawscout-ai-frontend:latest
    echo -e "${GREEN}✅ Frontend image pushed${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping push (no GITHUB_TOKEN)${NC}"
    echo "   Image built locally. To push manually:"
    echo "   docker push $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION"
    echo "   docker push $REGISTRY/$ORG/lawscout-ai-frontend:latest"
fi

cd ..

echo ""
echo "=================================="
echo -e "${GREEN}✅ Frontend Rebuilt!${NC}"
echo "=================================="
echo ""
echo "📝 Next Steps:"
echo "  1. Go to Render Dashboard → Frontend Service"
echo "  2. Update Docker image to: $REGISTRY/$ORG/lawscout-ai-frontend:latest"
echo "  3. Click 'Manual Deploy'"
echo "  4. Wait for deployment to complete"
echo "  5. Test at https://lawscoutai.com"
echo ""
echo "🔍 To verify the API URL is correct:"
echo "   After deployment, check browser console (F12) for:"
echo "   '🔍 Frontend API URL: $BACKEND_URL'"
echo ""




