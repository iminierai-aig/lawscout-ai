#!/bin/bash
# Deploy ONLY backend (faster for backend-only changes)

set -e

echo "🚀 LawScout AI - Backend Only Deployment"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set${NC}"
    echo "   export GITHUB_TOKEN=your_token"
    exit 1
fi

REGISTRY="ghcr.io"
ORG="iminierai-aig"
VERSION="v2.1.2"

# Login
echo "🔐 Logging in..."
echo "$GITHUB_TOKEN" | docker login $REGISTRY -u "$(git config user.name)" --password-stdin

# Build backend only
echo ""
echo "📦 Building Backend..."
cd backend

docker rmi $REGISTRY/$ORG/lawscout-ai-backend:$VERSION 2>/dev/null || true

echo "   Building with --no-cache to ensure fresh build..."
docker build \
    --no-cache \
    -t $REGISTRY/$ORG/lawscout-ai-backend:$VERSION . || {
    echo -e "${RED}❌ Backend build failed${NC}"
    exit 1
}

docker tag $REGISTRY/$ORG/lawscout-ai-backend:$VERSION \
           $REGISTRY/$ORG/lawscout-ai-backend:latest

echo "   Pushing..."
docker push $REGISTRY/$ORG/lawscout-ai-backend:$VERSION
docker push $REGISTRY/$ORG/lawscout-ai-backend:latest

echo ""
echo -e "${GREEN}✅ Backend deployed!${NC}"
echo ""
echo "Next steps:"
echo "1. Go to Dokploy"
echo "2. Restart the backend service (or it will auto-pull the new 'latest' image)"
echo "3. Make sure BACKEND_URL=https://api.lawscoutai.com is set in environment variables"
echo "4. Test OAuth at https://lawscoutai.com/login"

