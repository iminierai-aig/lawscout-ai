# Dokploy Frontend Deployment Guide

## Prerequisites

- ✅ Dokploy installed and running on your VPS
- ✅ GitHub repository connected to Dokploy
- ✅ Traefik configured for routing
- ✅ Backend API deployed and accessible at `https://api.lawscoutai.com`

---

## Step-by-Step Deployment

### 1. Create New Application in Dokploy

1. **Login to Dokploy**
   - Go to `https://dokploy.lawscoutai.com` (or your Dokploy URL)
   - Login with your credentials

2. **Create New Application**
   - Click **"New Application"** or **"+"** button
   - Select **"Docker"** as application type
   - Name it: `lawscout-frontend`

### 2. Configure Repository

1. **Connect Repository**
   - **Repository URL:** Your GitHub repo URL (e.g., `https://github.com/iminierai-aig/lawscout-ai`)
   - **Branch:** `main` or `feature/option-c-microservices` (your active branch)
   - **Dockerfile Path:** `frontend/Dockerfile`
   - **Docker Context:** `frontend/` (important!)

### 3. Configure Build Settings

**Build Arguments:**
```
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
```

**Build Command:** (Dokploy usually auto-detects, but verify)
- Should use: `docker build` with the Dockerfile

**Dockerfile Location:** `frontend/Dockerfile`

### 4. Configure Environment Variables

In Dokploy, go to **Environment Variables** section and add:

```bash
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
NODE_ENV=production
PORT=3000
```

**Important:** `NEXT_PUBLIC_API_URL` must be set as a **build argument** AND **environment variable** because Next.js bakes it into the build.

### 5. Configure Ports

- **Container Port:** `3000`
- **Host Port:** Leave empty (Traefik will handle routing)

### 6. Configure Traefik Labels (for routing)

Add these labels in Dokploy's **Labels** or **Traefik** section:

```yaml
traefik.enable: "true"
traefik.http.routers.frontend.rule: "Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
traefik.http.routers.frontend.entrypoints: "websecure"
traefik.http.routers.frontend.tls.certresolver: "letsencrypt"
traefik.http.services.frontend.loadbalancer.server.port: "3000"
```

### 7. Configure Health Check

- **Health Check Path:** `/` (or leave default)
- **Health Check Interval:** `30s`
- **Health Check Timeout:** `10s`

### 8. Resource Limits (Optional but Recommended)

- **Memory:** `512MB` (minimum) - `1GB` (recommended)
- **CPU:** `0.5` cores minimum

### 9. Deploy

1. Click **"Save"** or **"Deploy"**
2. Dokploy will:
   - Clone your repository
   - Build the Docker image using `frontend/Dockerfile`
   - Start the container
   - Configure Traefik routing

### 10. Verify Deployment

1. **Check Logs:**
   - Go to **Logs** tab in Dokploy
   - Look for: "Ready on http://localhost:3000"

2. **Test Frontend:**
   ```bash
   curl https://lawscoutai.com
   curl https://www.lawscoutai.com
   ```

3. **Check Browser:**
   - Visit `https://lawscoutai.com`
   - Open browser console
   - Should see: `🔍 Frontend API URL: https://api.lawscoutai.com`

---

## Troubleshooting

### Build Fails

**Error: "Cannot find module"**
- Check that `package.json` is in the `frontend/` directory
- Verify Docker context is set to `frontend/`

**Error: "NEXT_PUBLIC_API_URL not found"**
- Ensure build argument is set: `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com`
- Rebuild the application

### Container Won't Start

**Error: "Cannot find server.js"**
- The Dockerfile expects standalone output
- Verify `next.config.js` has `output: 'standalone'`
- Check build logs for errors

**Error: "Port already in use"**
- Another service might be using port 3000
- Check Dokploy for other applications on port 3000

### Routing Issues

**404 Not Found**
- Check Traefik labels are correct
- Verify domain DNS points to your VPS IP
- Check Traefik logs: `docker logs traefik`

**CORS Errors**
- Verify backend CORS includes `https://lawscoutai.com` and `https://www.lawscoutai.com`
- Check browser console for specific CORS error

### API Connection Issues

**"Cannot connect to backend"**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Test backend directly: `curl https://api.lawscoutai.com/health`
- Check browser console for API URL being used

---

## Quick Reference

### Dokploy Configuration Summary

| Setting | Value |
|---------|-------|
| **Application Type** | Docker |
| **Repository** | Your GitHub repo |
| **Branch** | `main` or your branch |
| **Dockerfile Path** | `frontend/Dockerfile` |
| **Docker Context** | `frontend/` |
| **Build Args** | `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com` |
| **Port** | `3000` |
| **Environment** | `NODE_ENV=production` |

### Traefik Labels

```yaml
traefik.enable: "true"
traefik.http.routers.frontend.rule: "Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
traefik.http.routers.frontend.entrypoints: "websecure"
traefik.http.routers.frontend.tls.certresolver: "letsencrypt"
traefik.http.services.frontend.loadbalancer.server.port: "3000"
```

---

## Post-Deployment Checklist

- [ ] Frontend accessible at `https://lawscoutai.com`
- [ ] Frontend accessible at `https://www.lawscoutai.com`
- [ ] Browser console shows correct API URL
- [ ] Login/Register pages work
- [ ] Search functionality works
- [ ] Auth system working (can register/login)
- [ ] Search limits enforced
- [ ] SSL certificate valid (green lock in browser)
- [ ] No console errors

---

## Updating Frontend

To update the frontend after code changes:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update frontend"
   git push
   ```

2. **Redeploy in Dokploy:**
   - Go to your application in Dokploy
   - Click **"Redeploy"** or **"Deploy"**
   - Dokploy will pull latest code and rebuild

**Note:** If you change `NEXT_PUBLIC_API_URL`, you must rebuild (not just restart) because it's baked into the build.

---

## Alternative: Manual Docker Build

If Dokploy doesn't work, you can build and deploy manually:

```bash
# On your VPS
cd /path/to/lawscout-ai/frontend

# Build
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.lawscoutai.com \
  -t lawscout-frontend:latest .

# Run
docker run -d \
  --name lawscout-frontend \
  --network traefik-network \
  -p 3000:3000 \
  -e NODE_ENV=production \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.frontend.rule=Host(\`lawscoutai.com\`) || Host(\`www.lawscoutai.com\`)" \
  --label "traefik.http.routers.frontend.entrypoints=websecure" \
  --label "traefik.http.routers.frontend.tls.certresolver=letsencrypt" \
  --label "traefik.http.services.frontend.loadbalancer.server.port=3000" \
  lawscout-frontend:latest
```

---

**Last Updated:** December 2024  
**Status:** Ready for deployment

