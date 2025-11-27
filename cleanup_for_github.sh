#!/bin/bash
# Cleanup script for preparing LawScout AI for GitHub

set -e

echo "🧹 Cleaning up LawScout AI for GitHub..."
echo "========================================"
echo ""

# Remove backup files
echo "📦 Removing backup files..."
find . -type f \( -name "*.bak" -o -name "*.OLD" -o -name "*.backup" \) \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -delete 2>/dev/null || true
echo "✅ Backup files removed"

# Remove log files
echo "📋 Removing log files..."
rm -f *.log collection_100k.log 2>/dev/null || true
echo "✅ Log files removed"

# Remove backup directory
echo "🗂️  Removing backup directory..."
rm -rf lawscout-ai.backup/ 2>/dev/null || true
echo "✅ Backup directory removed"

# Remove Python cache
echo "🐍 Removing Python cache..."
find . -type d -name "__pycache__" \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -delete 2>/dev/null || true
echo "✅ Python cache removed"

# Check for large files
echo ""
echo "📊 Checking for large files (>10MB)..."
LARGE_FILES=$(find . -type f -size +10M \
    -not -path "./.venv/*" \
    -not -path "./.git/*" \
    -not -path "./data/*" \
    -not -path "./qdrant_storage/*" \
    2>/dev/null | head -10)

if [ -z "$LARGE_FILES" ]; then
    echo "✅ No large files found (excluding data/ and qdrant_storage/)"
else
    echo "⚠️  Found large files:"
    echo "$LARGE_FILES"
    echo "Consider adding these to .gitignore if they shouldn't be committed"
fi

echo ""
echo "========================================"
echo "✅ Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Review .gitignore to ensure all sensitive/large files are excluded"
echo "2. Run: git status (to see what will be committed)"
echo "3. Run: git add ."
echo "4. Run: git commit -m 'Initial commit'"
echo "5. Create GitHub repo and push"
echo ""
echo "⚠️  Remember to:"
echo "   - Never commit .env files"
echo "   - Never commit API keys or secrets"
echo "   - Data files are excluded (they're large)"
echo "   - Qdrant storage is excluded (local database)"

