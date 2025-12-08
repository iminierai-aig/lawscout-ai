# Quick Deployment Guide

## ✅ Repository Cleanup Complete

All temporary files have been moved to `history/` directory. The repository is ready for deployment.

## 🚀 Deployment Steps

### Step 1: Commit and Push Code

```bash
# Review changes
git status

# Commit all changes
git commit -m "Deploy v2.1.1: Next.js frontend, performance logging, cleanup"

# Push to GitHub
git push origin <your-branch-name>
```

### Step 2: Build and Push Docker Images

```bash
# Set GitHub token (if not already set)
export GITHUB_TOKEN=your_github_personal_access_token

# Run deployment script
./scripts/deploy.sh
```

This will:
- Build backend image: `ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.1`
- Build frontend image: `ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.1`
- Push both images to GitHub Container Registry

### Step 3: Deploy to Render.com

1. **Backend Service:**
   - Go to Render Dashboard → Backend Service
   - Update Docker image to: `ghcr.io/iminierai-aig/lawscout-ai-backend:latest`
   - Verify environment variables:
     - `QDRANT_URL`
     - `QDRANT_API_KEY`
     - `GEMINI_API_KEY`
     - `PORT=8000`
   - Click "Manual Deploy" or wait for auto-deploy

2. **Frontend Service:**
   - Go to Render Dashboard → Frontend Service
   - Update Docker image to: `ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`
   - Verify environment variables:
     - `NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com`
     - `NODE_ENV=production`
     - `PORT=3000`
   - Click "Manual Deploy" or wait for auto-deploy

### Step 4: Verify Deployment

```bash
# Check backend health
curl https://your-backend-url.onrender.com/health

# Check frontend
curl https://your-frontend-url.onrender.com
```

## 📋 What's New in v2.1.1

- ✅ Next.js frontend with Harvey.ai-inspired design
- ✅ Sidebar with query history and settings
- ✅ Performance logging (search/generation times)
- ✅ Clickable source links
- ✅ History management (delete items, clear all)
- ✅ Repository cleanup (temporary files moved to history/)

## 📊 Performance

- **Search Time:** ~1.5s
- **Generation Time:** ~8s (Gemini API)
- **Total Response:** ~9-10s

## 🔧 Troubleshooting

If deployment fails:

1. Check Render logs for errors
2. Verify environment variables are set correctly
3. Check Docker image tags match
4. Verify backend health endpoint: `/health`

For detailed instructions, see `DEPLOYMENT.md`.

