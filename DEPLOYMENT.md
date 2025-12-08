# Deployment Guide - LawScout AI v2.1.1

## Prerequisites

1. **GitHub Container Registry Access**
   - GitHub Personal Access Token with `write:packages` scope
   - Docker installed and running

2. **Render.com Account**
   - Backend service configured
   - Frontend service configured
   - Environment variables set

## Step 1: Build and Push Docker Images

### Backend Image

```bash
cd backend

# Build the image
docker build -t ghcr.io/iminierai-aig/lawscout-ai-backend:latest .
docker build -t ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.1 .

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push images
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:latest
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.1
```

### Frontend Image

```bash
cd frontend

# Build the image
docker build -t ghcr.io/iminierai-aig/lawscout-ai-frontend:latest .
docker build -t ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.1 .

# Push images
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.1
```

## Step 2: Update Render.com Services

### Backend Service

1. Go to Render Dashboard → Backend Service
2. Update Docker image:
   - Image: `ghcr.io/iminierai-aig/lawscout-ai-backend:latest`
   - Or use specific version: `ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.1`

3. Environment Variables (verify these are set):
   ```
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_key
   GEMINI_API_KEY=your_gemini_key
   PORT=8000
   ```

4. Health Check:
   - Path: `/health`
   - Should return: `{"status": "healthy", ...}`

### Frontend Service

1. Go to Render Dashboard → Frontend Service
2. Update Docker image:
   - Image: `ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`
   - Or use specific version: `ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.1`

3. Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   NODE_ENV=production
   PORT=3000
   ```

4. Health Check:
   - Path: `/`
   - Should return: 200 OK

## Step 3: Deploy

1. **Manual Deploy** (recommended for first deployment):
   - Render Dashboard → Manual Deploy
   - Select the service
   - Click "Deploy latest commit"

2. **Auto Deploy** (for future updates):
   - Render will auto-deploy when you push to main branch
   - Or when you update the Docker image tag

## Step 4: Verify Deployment

### Backend Health Check
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "rag_engine": "initialized",
  "memory_mb": <number>,
  "memory_warning": false
}
```

### Frontend Check
```bash
curl https://your-frontend-url.onrender.com
```

Should return: 200 OK with HTML

### Test Search
```bash
curl -X POST https://your-backend-url.onrender.com/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "test query",
    "collection": "both",
    "limit": 5
  }'
```

## Rollback (if needed)

If something goes wrong:

```bash
# Revert to previous version
docker pull ghcr.io/iminierai-aig/lawscout-ai-backend:v2.0.0
docker tag ghcr.io/iminierai-aig/lawscout-ai-backend:v2.0.0 \
           ghcr.io/iminierai-aig/lawscout-ai-backend:latest
docker push ghcr.io/iminierai-aig/lawscout-ai-backend:latest

# Then trigger Render redeploy
```

## Performance Expectations

- **Search Time:** ~1.5s (very fast)
- **Generation Time:** ~8s (Gemini API - expected)
- **Total Response:** ~9-10s (acceptable for high-quality AI answers)

## Monitoring

- Check Render Dashboard for service health
- Monitor logs: `backend/logs/backend.log` (if accessible)
- Check memory usage via `/health` endpoint

