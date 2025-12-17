#!/bin/bash
# Prepare repository for deployment
# Stages all changes and shows what will be committed

set -e

echo "📋 Preparing repository for deployment..."
echo ""

# Add all modified and new files (respecting .gitignore)
git add -A

echo "✅ Files staged"
echo ""
echo "📝 Changes to be committed:"
git status --short
echo ""

# Show summary
echo "📊 Summary:"
echo "  Modified files: $(git diff --cached --name-only | wc -l | tr -d ' ')"
echo "  New files: $(git diff --cached --diff-filter=A --name-only | wc -l | tr -d ' ')"
echo ""

read -p "Ready to commit? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "💡 Next steps:"
    echo "  1. Review changes: git diff --cached"
    echo "  2. Commit: git commit -m 'Deploy v2.1.1: Next.js frontend, performance logging, cleanup'"
    echo "  3. Push: git push origin <branch-name>"
    echo "  4. Build images: ./scripts/deploy.sh"
    echo "  5. Deploy to Render: See DEPLOYMENT.md"
else
    echo "❌ Cancelled. Review changes with: git status"
fi

