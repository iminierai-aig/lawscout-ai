#!/bin/bash
# Deploy ONLY frontend (faster for UI-only changes)

set -e

echo "🚀 LawScout AI - Frontend Only Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set${NC}"
    echo "   export GITHUB_TOKEN=your_token"
    exit 1
fi

REGISTRY="ghcr.io"
ORG="iminierai-aig"
VERSION="v2.1.1"

# Login
echo "🔐 Logging in..."
echo "$GITHUB_TOKEN" | docker login $REGISTRY -u "$(git config user.name)" --password-stdin

# Build frontend only
echo ""
echo "📦 Building Frontend..."
cd frontend

docker rmi $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION 2>/dev/null || true

BACKEND_URL="${BACKEND_URL:-https://api.lawscoutai.com}"
echo "   Backend URL: $BACKEND_URL"

docker build \
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
    -t $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION .

docker tag $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION \
           $REGISTRY/$ORG/lawscout-ai-frontend:latest

echo "   Pushing..."
docker push $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION
docker push $REGISTRY/$ORG/lawscout-ai-frontend:latest

echo ""
echo -e "${GREEN}✅ Frontend deployed!${NC}"
echo ""
echo "Deploy to your VPS using Dokploy or your deployment method"