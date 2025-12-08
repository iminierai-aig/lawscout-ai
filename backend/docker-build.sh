#!/bin/bash
# Docker Build Script for LawScout Backend with Versioning
# Builds and tags Docker images with proper versioning

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="lawscout-backend"
REGISTRY="ghcr.io/iminierai-aig"
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}"

# Get version from argument or prompt
VERSION="${1:-}"

if [ -z "$VERSION" ]; then
    # Try to get version from git tag or use default
    if git describe --tags --exact-match HEAD 2>/dev/null; then
        VERSION=$(git describe --tags --exact-match HEAD)
    else
        # Default versioning scheme: v2.1.X
        LAST_VERSION=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Tag}}" 2>/dev/null | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+$" | sort -V | tail -1 || echo "v2.1.1")
        
        # Increment patch version
        MAJOR_MINOR=$(echo "$LAST_VERSION" | cut -d. -f1-2)
        PATCH=$(echo "$LAST_VERSION" | cut -d. -f3 | sed 's/v//')
        NEW_PATCH=$((PATCH + 1))
        VERSION="${MAJOR_MINOR}.${NEW_PATCH}"
        
        echo -e "${YELLOW}No version specified. Auto-incrementing to: ${VERSION}${NC}"
        read -p "Use this version? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            read -p "Enter version (e.g., v2.1.2): " VERSION
        fi
    fi
fi

# Ensure version starts with 'v'
if [[ ! "$VERSION" =~ ^v ]]; then
    VERSION="v${VERSION}"
fi

echo ""
echo -e "${BLUE}🏗️  Building LawScout Backend Docker Image${NC}"
echo "=========================================="
echo -e "Image: ${GREEN}${IMAGE_NAME}${NC}"
echo -e "Version: ${GREEN}${VERSION}${NC}"
echo -e "Registry: ${GREEN}${REGISTRY}${NC}"
echo ""

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ Error: Dockerfile not found${NC}"
    exit 1
fi

# Build the image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build \
    --tag "${IMAGE_NAME}:${VERSION}" \
    --tag "${IMAGE_NAME}:latest" \
    --tag "${FULL_IMAGE_NAME}:${VERSION}" \
    --tag "${FULL_IMAGE_NAME}:latest" \
    --progress=plain \
    .

# Show image size
echo ""
echo -e "${GREEN}✅ Build complete!${NC}"
echo ""
echo "📊 Image details:"
docker images "${IMAGE_NAME}:${VERSION}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
echo ""

# Ask if user wants to push
read -p "Push to registry? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}📤 Pushing images to ${REGISTRY}...${NC}"
    docker push "${FULL_IMAGE_NAME}:${VERSION}"
    docker push "${FULL_IMAGE_NAME}:latest"
    echo -e "${GREEN}✅ Push complete!${NC}"
fi

echo ""
echo -e "${GREEN}✅ All done!${NC}"
echo ""
echo "Usage:"
echo "  docker run -p 8000:8000 ${IMAGE_NAME}:${VERSION}"
echo "  docker run -p 8000:8000 ${FULL_IMAGE_NAME}:${VERSION}"

