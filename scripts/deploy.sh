#!/bin/bash
# Deployment script for LawScout AI v2.1.1
# Builds and pushes Docker images to GitHub Container Registry

set -e

echo "🚀 LawScout AI Deployment Script"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN not set${NC}"
    echo "   Set it with: export GITHUB_TOKEN=your_token"
    echo "   Or create a Personal Access Token at: https://github.com/settings/tokens"
    echo "   Required scope: write:packages"
    exit 1
fi

# GitHub Container Registry
REGISTRY="ghcr.io"
ORG="iminierai-aig"
VERSION="v2.1.1"

# Login to GitHub Container Registry
echo "🔐 Logging in to GitHub Container Registry..."
echo "$GITHUB_TOKEN" | docker login $REGISTRY -u "$(git config user.name)" --password-stdin || {
    echo -e "${RED}❌ Failed to login to GitHub Container Registry${NC}"
    exit 1
}
echo -e "${GREEN}✅ Logged in${NC}"
echo ""

# Build and push backend
echo "📦 Building Backend Image..."
cd backend

# Clean up old version if it exists locally
echo "   Cleaning up old local images (if any)..."
docker rmi $REGISTRY/$ORG/lawscout-ai-backend:$VERSION 2>/dev/null || true
docker rmi lawscout-backend:$VERSION 2>/dev/null || true

echo "   Building: $REGISTRY/$ORG/lawscout-ai-backend:$VERSION"
docker build -t $REGISTRY/$ORG/lawscout-ai-backend:$VERSION . || {
    echo -e "${RED}❌ Backend build failed${NC}"
    exit 1
}

echo "   Tagging as latest..."
docker tag $REGISTRY/$ORG/lawscout-ai-backend:$VERSION \
           $REGISTRY/$ORG/lawscout-ai-backend:latest

echo "   Pushing to registry..."
docker push $REGISTRY/$ORG/lawscout-ai-backend:$VERSION
docker push $REGISTRY/$ORG/lawscout-ai-backend:latest

echo -e "${GREEN}✅ Backend image pushed${NC}"
echo ""

# Build and push frontend
echo "📦 Building Frontend Image..."
cd ../frontend

# Clean up old version if it exists locally
echo "   Cleaning up old local images (if any)..."
docker rmi $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION 2>/dev/null || true
docker rmi lawscout-frontend:$VERSION 2>/dev/null || true

echo "   Building: $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION"
# Get backend URL from environment or use default
BACKEND_URL="${BACKEND_URL:-https://api.lawscoutai.com}"
echo "   Using backend URL: $BACKEND_URL"
docker build \
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL \
    -t $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION . || {
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
}

echo "   Tagging as latest..."
docker tag $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION \
           $REGISTRY/$ORG/lawscout-ai-frontend:latest

echo "   Pushing to registry..."
docker push $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION
docker push $REGISTRY/$ORG/lawscout-ai-frontend:latest

echo -e "${GREEN}✅ Frontend image pushed${NC}"
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}✅ Deployment Images Ready!${NC}"
echo "=================================="
echo ""
echo "Backend Image:"
echo "  - $REGISTRY/$ORG/lawscout-ai-backend:$VERSION"
echo "  - $REGISTRY/$ORG/lawscout-ai-backend:latest"
echo ""
echo "Frontend Image:"
echo "  - $REGISTRY/$ORG/lawscout-ai-frontend:$VERSION"
echo "  - $REGISTRY/$ORG/lawscout-ai-frontend:latest"
echo ""
echo "📝 Next Steps:"
echo "  1. Go to Render Dashboard"
echo "  2. Update backend service to use: $REGISTRY/$ORG/lawscout-ai-backend:latest"
echo "  3. Update frontend service to use: $REGISTRY/$ORG/lawscout-ai-frontend:latest"
echo "  4. Trigger manual deploy or wait for auto-deploy"
echo ""
echo "📖 See DEPLOYMENT.md for detailed instructions"

