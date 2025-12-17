# Cleaning Up GitHub Container Registry Packages

Guide for removing old Docker images from `ghcr.io/iminierai-aig/`

## Method 1: GitHub Web UI (Easiest)

1. **Go to your GitHub repository:**
   - Navigate to: `https://github.com/iminierai-aig/lawscout-ai`
   - Or go to: `https://github.com/iminierai-aig?tab=packages`

2. **Find the package:**
   - Click on "Packages" in the repository navigation
   - Or go directly to: `https://github.com/orgs/iminierai-aig/packages`

3. **Select the package:**
   - Click on `lawscout-ai-backend` or `lawscout-ai-frontend`
   - You'll see all versions/tags

4. **Delete specific versions:**
   - Click on the version you want to delete (e.g., `v2.1.0`)
   - Scroll down and click "Delete version"
   - Confirm deletion

5. **Delete entire package (if needed):**
   - Go to package settings
   - Scroll to "Danger Zone"
   - Click "Delete this package"

## Method 2: GitHub API (Command Line)

### Delete a specific version/tag

```bash
# Set variables
ORG="iminierai-aig"
PACKAGE_NAME="lawscout-ai-backend"  # or "lawscout-ai-frontend"
VERSION="v2.1.0"  # version to delete
GITHUB_TOKEN="your_github_personal_access_token"

# Get package version ID
PACKAGE_VERSION_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/$ORG/packages/container/$PACKAGE_NAME/versions" \
  | jq -r ".[] | select(.metadata.container.tags[] == \"$VERSION\") | .id")

# Delete the version
curl -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/$ORG/packages/container/$PACKAGE_NAME/versions/$PACKAGE_VERSION_ID"
```

### List all versions

```bash
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/$ORG/packages/container/$PACKAGE_NAME/versions" \
  | jq -r '.[] | "\(.id) - \(.metadata.container.tags[])"'
```

## Method 3: Clean Up Script

Create a script to clean up old versions:

```bash
#!/bin/bash
# Clean up old Docker image versions from GitHub Container Registry

set -e

# Configuration
ORG="iminierai-aig"
PACKAGE_NAME="${1:-lawscout-ai-backend}"  # Default to backend
KEEP_VERSIONS="${2:-3}"  # Keep last N versions
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set"
    echo "   Set it with: export GITHUB_TOKEN=your_token"
    exit 1
fi

echo "🧹 Cleaning up old versions of $PACKAGE_NAME..."
echo "   Keeping last $KEEP_VERSIONS versions"
echo ""

# Get all versions (sorted by creation date, newest first)
VERSIONS=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/orgs/$ORG/packages/container/$PACKAGE_NAME/versions" \
  | jq -r 'sort_by(.created_at) | reverse | .[] | "\(.id)|\(.metadata.container.tags[])"')

# Count total versions
TOTAL=$(echo "$VERSIONS" | wc -l | tr -d ' ')
echo "📊 Found $TOTAL versions"

# Skip the first KEEP_VERSIONS and delete the rest
echo "$VERSIONS" | tail -n +$((KEEP_VERSIONS + 1)) | while IFS='|' read -r ID TAG; do
    if [ -n "$ID" ] && [ -n "$TAG" ]; then
        echo "🗑️  Deleting $TAG (ID: $ID)..."
        curl -X DELETE -s \
          -H "Authorization: token $GITHUB_TOKEN" \
          -H "Accept: application/vnd.github.v3+json" \
          "https://api.github.com/orgs/$ORG/packages/container/$PACKAGE_NAME/versions/$ID" \
          && echo "   ✅ Deleted $TAG" || echo "   ❌ Failed to delete $TAG"
    fi
done

echo ""
echo "✅ Cleanup complete!"
```

## Method 4: Clean Local Docker Images

To clean up local Docker images (not from registry):

```bash
# Remove specific version
docker rmi ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.0

# Remove all lawscout images except latest
docker images | grep lawscout | grep -v latest | awk '{print $1":"$2}' | xargs docker rmi

# Remove dangling images
docker image prune -f

# Remove all unused images
docker image prune -a -f
```

## Quick Reference

### Delete via Web UI:
1. Go to: `https://github.com/orgs/iminierai-aig/packages`
2. Click package → Click version → Delete version

### Delete via API:
```bash
# Single version
curl -X DELETE \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/orgs/iminierai-aig/packages/container/LAWSCOUT-AI-BACKEND/versions/VERSION_ID"
```

### Required GitHub Token Permissions:
- `delete:packages` - To delete packages
- `read:packages` - To list packages

## Notes

- **Deleting packages is permanent** - cannot be undone
- **Free tier limits**: GitHub allows limited storage for packages
- **Keep at least 2-3 versions** for rollback capability
- **`latest` tag** is just a pointer - deleting it doesn't delete the image

