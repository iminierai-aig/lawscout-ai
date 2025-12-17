# Dokploy Frontend Deployment - Quick Start

## 🚀 Quick Deployment Steps

### 1. In Dokploy Dashboard

**Create New Application:**
- Type: **Docker**
- Name: `lawscout-frontend`

### 2. Repository Settings

```
Repository URL: https://github.com/iminierai-aig/lawscout-ai
Branch: feature/option-c-microservices (or your branch)
Dockerfile Path: frontend/Dockerfile
Docker Context: frontend/
```

### 3. Build Arguments (CRITICAL!)

```
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
```

**⚠️ IMPORTANT:** This MUST be set as a build argument, not just an environment variable!

### 4. Environment Variables

```
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
NODE_ENV=production
PORT=3000
```

### 5. Port Configuration

```
Container Port: 3000
Host Port: (leave empty - Traefik handles routing)
```

### 6. Traefik Labels

Add these in the Labels/Traefik section:

```
traefik.enable = true
traefik.http.routers.frontend.rule = Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)
traefik.http.routers.frontend.entrypoints = websecure
traefik.http.routers.frontend.tls.certresolver = letsencrypt
traefik.http.services.frontend.loadbalancer.server.port = 3000
```

### 7. Deploy!

Click **"Deploy"** and wait for build to complete.

---

## ✅ Verification

After deployment:

1. **Check Logs** - Should see "Ready on http://localhost:3000"
2. **Visit** `https://lawscoutai.com`
3. **Open Browser Console** - Should see: `🔍 Frontend API URL: https://api.lawscoutai.com`
4. **Test Login** - Try registering/logging in

---

## 🐛 Common Issues

**Build fails:**
- Check Dockerfile path is `frontend/Dockerfile`
- Check Docker context is `frontend/`
- Verify `NEXT_PUBLIC_API_URL` is set as build argument

**Container won't start:**
- Check logs for errors
- Verify port 3000 is not in use
- Check that `server.js` exists (should be created by Next.js build)

**404 errors:**
- Verify Traefik labels are correct
- Check DNS points to your VPS
- Verify Traefik is running

**API connection fails:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is accessible at `https://api.lawscoutai.com`
- Check browser console for API URL

---

## 📝 Notes

- The Dockerfile uses Next.js standalone output
- `NEXT_PUBLIC_API_URL` is baked into the build - changes require rebuild
- Traefik handles SSL/TLS automatically
- Health check runs every 30 seconds

