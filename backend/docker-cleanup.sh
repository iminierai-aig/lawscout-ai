#!/bin/bash
# Docker Cleanup Script for LawScout Backend
# Removes old/unused Docker images and containers

set -e

echo "🧹 LawScout Backend - Docker Cleanup"
echo "===================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Image patterns to clean
IMAGE_PATTERNS=(
    "lawscout-backend"
    "ghcr.io/iminierai-aig/lawscout-backend"
)

# Function to show disk usage
show_disk_usage() {
    echo "📊 Current Docker disk usage:"
    docker system df
    echo ""
}

# Function to remove old images
cleanup_images() {
    echo "🗑️  Removing old lawscout-backend images..."
    
    for pattern in "${IMAGE_PATTERNS[@]}"; do
        echo "  Checking: $pattern"
        
        # List images matching pattern
        images=$(docker images "$pattern" --format "{{.ID}} {{.Repository}}:{{.Tag}}" 2>/dev/null || true)
        
        if [ -z "$images" ]; then
            echo "    No images found for $pattern"
            continue
        fi
        
        # Keep latest and newest version, remove old large images
        echo "$images" | while read -r id repo_tag; do
            # Keep latest and versions >= v2.1.2 (optimized)
            if [[ "$repo_tag" == *"latest"* ]] || [[ "$repo_tag" == *"v2.1.2"* ]] || [[ "$repo_tag" == *"v2.1.3"* ]] || [[ "$repo_tag" == *"v2.1.4"* ]] || [[ "$repo_tag" == *"v2.1.5"* ]] || [[ "$repo_tag" == *"v2.2"* ]]; then
                echo "    Keeping: $repo_tag"
            else
                echo "    Removing: $repo_tag ($id)"
                docker rmi "$id" 2>/dev/null || echo "      (already removed or in use)"
            fi
        done
    done
    echo ""
}

# Function to remove dangling images
cleanup_dangling() {
    echo "🗑️  Removing dangling images..."
    docker image prune -f
    echo ""
}

# Function to remove stopped containers
cleanup_containers() {
    echo "🗑️  Removing stopped containers..."
    docker container prune -f
    echo ""
}

# Function to remove unused volumes
cleanup_volumes() {
    echo "🗑️  Removing unused volumes..."
    docker volume prune -f
    echo ""
}

# Function to remove unused networks
cleanup_networks() {
    echo "🗑️  Removing unused networks..."
    docker network prune -f
    echo ""
}

# Function to full system cleanup (aggressive)
full_cleanup() {
    echo "⚠️  Performing full system cleanup (removes all unused resources)..."
    read -p "This will remove ALL unused Docker resources. Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -a -f --volumes
        echo "✅ Full cleanup complete"
    else
        echo "❌ Full cleanup cancelled"
    fi
    echo ""
}

# Main menu
show_disk_usage

echo "Select cleanup option:"
echo "1) Remove old lawscout-backend images (keeps latest and v2.1.1)"
echo "2) Remove dangling images"
echo "3) Remove stopped containers"
echo "4) Remove unused volumes"
echo "5) Remove unused networks"
echo "6) All of the above (safe cleanup)"
echo "7) Full system cleanup (aggressive - removes everything unused)"
echo "8) Exit"
echo ""

read -p "Choice [1-8]: " choice

case $choice in
    1)
        cleanup_images
        ;;
    2)
        cleanup_dangling
        ;;
    3)
        cleanup_containers
        ;;
    4)
        cleanup_volumes
        ;;
    5)
        cleanup_networks
        ;;
    6)
        cleanup_images
        cleanup_dangling
        cleanup_containers
        cleanup_volumes
        cleanup_networks
        echo "✅ Safe cleanup complete"
        ;;
    7)
        full_cleanup
        ;;
    8)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Show final disk usage
echo ""
show_disk_usage

echo "✅ Cleanup complete!"

