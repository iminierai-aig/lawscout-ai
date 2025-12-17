#!/bin/bash
# Clean up old Docker images for LawScout AI

set -e

echo "🧹 Cleaning up LawScout AI Docker Images..."
echo ""

# Colors
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# List current images
echo "📋 Current LawScout images:"
docker images | grep lawscout || echo "   No images found"
echo ""

# Ask which version to remove
read -p "Enter version to remove (e.g., v2.1.1) or 'all' for all old versions: " VERSION

if [ "$VERSION" = "all" ]; then
    echo -e "${YELLOW}⚠️  This will remove ALL LawScout images except 'latest'${NC}"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing all versioned images..."
        docker images | grep lawscout | grep -v latest | awk '{print $1":"$2}' | xargs -r docker rmi || true
        echo -e "${GREEN}✅ Cleanup complete${NC}"
    else
        echo "❌ Cancelled"
    fi
elif [ -n "$VERSION" ]; then
    echo "🗑️  Removing version $VERSION..."
    
    # Remove both naming conventions
    docker rmi lawscout-backend:$VERSION 2>/dev/null || true
    docker rmi lawscout-frontend:$VERSION 2>/dev/null || true
    docker rmi ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION 2>/dev/null || true
    docker rmi ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION 2>/dev/null || true
    
    echo -e "${GREEN}✅ Removed $VERSION images${NC}"
else
    echo "❌ No version specified"
    exit 1
fi

echo ""
echo "📋 Remaining images:"
docker images | grep lawscout || echo "   No images found"

