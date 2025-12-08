#!/bin/bash
# Clean up repository - remove unnecessary files

set -e

echo "🧹 Cleaning up repository..."
echo ""

# Move temporary docs to history
if [ -d "history" ]; then
    echo "📁 Moving temporary docs to history/..."
    mkdir -p history
    mv LOCAL_TESTING*.md frontend/ENHANCEMENTS.md backend/DOCKER_*.md backend/PERFORMANCE_*.md backend/RENDER_*.md history/ 2>/dev/null || true
    echo "✅ Moved temporary docs"
fi

# Remove build artifacts (should be in .gitignore, but just in case)
echo "🗑️  Removing build artifacts..."
rm -rf frontend/.next
rm -rf frontend/node_modules
rm -rf backend/__pycache__
rm -rf backend/**/__pycache__
rm -rf backend/venv
rm -rf backend/logs/*.log 2>/dev/null || true
echo "✅ Removed build artifacts"

# Remove temporary scripts (keep in scripts/)
echo "📝 Organizing scripts..."
# Scripts are already in scripts/ directory

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📋 Files ready to commit:"
git status --short | grep -v "^??" | head -20

