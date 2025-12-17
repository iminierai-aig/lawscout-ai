# Manual Deployment Commands

Step-by-step commands to manually build and push Docker images (if you've already logged in to ghcr.io).

## Prerequisites

1. **Already logged in to GitHub Container Registry:**
   ```bash
   docker login ghcr.io -u YOUR_GITHUB_USERNAME
   ```

2. **Set version variable:**
   ```bash
   export VERSION="v2.1.1"
   ```

## Step 1: Clean Up Old Local Images (Optional)

```bash
# Remove old backend v2.1.1 if it exists
docker rmi ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.1 2>/dev/null || true
docker rmi lawscout-backend:v2.1.1 2>/dev/null || true

# Remove old frontend v2.1.1 if it exists
docker rmi ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.1 2>/dev/null || true
docker rmi lawscout-frontend:v2.1.1 2>/dev/null || true
```

## Step 2: Build Backend Image

```bash
# Navigate to backend directory
cd backend

# Build the image with version tag
docker build -t ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION .

# Tag as latest
docker tag ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION \
           ghcr.io/iminierai-aig/lawscout-ai-backend:latest
```

## Step 3: Push Backend Image

```bash
# Push versioned image
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION

# Push latest tag
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:latest
```

## Step 4: Build Frontend Image

```bash
# Navigate to frontend directory
cd ../frontend

# Build the image with version tag
docker build -t ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION .

# Tag as latest
docker tag ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION \
           ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
```

## Step 5: Push Frontend Image

```bash
# Push versioned image
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION

# Push latest tag
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
```

## Complete Command Sequence

Here's the complete sequence you can copy-paste:

```bash
# Set version
export VERSION="v2.1.1"

# Clean up old images (optional)
docker rmi ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION 2>/dev/null || true
docker rmi ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION 2>/dev/null || true

# Build and push backend
cd backend
docker build -t ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION .
docker tag ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION \
           ghcr.io/iminierai-aig/lawscout-ai-backend:latest
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:$VERSION
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:latest

# Build and push frontend
cd ../frontend
docker build -t ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION .
docker tag ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION \
           ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:$VERSION
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:latest

# Return to project root
cd ..
```

## Verify Images

After pushing, verify the images are in the registry:

```bash
# List local images
docker images | grep lawscout

# Or check on GitHub:
# Go to: https://github.com/iminierai-aig?tab=packages
```

## Next Steps

After images are pushed:

1. Go to Render Dashboard
2. Update backend service to use: `ghcr.io/iminierai-aig/lawscout-ai-backend:latest`
3. Update frontend service to use: `ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`
4. Trigger manual deploy or wait for auto-deploy

