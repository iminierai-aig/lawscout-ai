# Fixing Dokploy Compose Frontend Deployment

## Problem

Your current setup uses a pre-built Docker image:
```yaml
image: ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
```

But `NEXT_PUBLIC_API_URL` is set as an **environment variable**, which doesn't work because Next.js bakes these variables into the build at **build time**, not runtime.

## Solution Options

### Option 1: Rebuild and Push Image (Recommended)

Rebuild the frontend image with the correct API URL and push it to GitHub Container Registry.

**Steps:**

1. **Rebuild the image locally or in CI:**
   ```bash
   cd /path/to/lawscout-ai
   
   # Set your GitHub token
   export GITHUB_TOKEN=your_token
   
   # Run the deployment script (rebuilds with correct API URL)
   ./scripts/deploy.sh
   ```

   Or manually:
   ```bash
   cd frontend
   docker build \
     --build-arg NEXT_PUBLIC_API_URL=https://api.lawscoutai.com \
     -t ghcr.io/iminierai-aig/lawscout-ai-frontend:latest .
   
   docker push ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
   ```

2. **Update the Compose File:**
   ```yaml
   version: '3.8'
   
   services:
     frontend:
       image: ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
       container_name: lawscout-frontend
       environment:
         - NODE_ENV=production
         - PORT=3000
       networks:
         - dokploy-network
       restart: unless-stopped
       labels:
         - "traefik.enable=true"
         - "traefik.http.routers.frontend.rule=Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
         - "traefik.http.routers.frontend.entrypoints=websecure"
         - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
         - "traefik.http.services.frontend.loadbalancer.server.port=3000"
   
   networks:
     dokploy-network:
       external: true
   ```

3. **Redeploy in Dokploy:**
   - Pull the updated image
   - Restart the service

**Pros:**
- ✅ Keeps using pre-built images (faster deployments)
- ✅ Image is built once, deployed many times
- ✅ Works with your current compose setup

**Cons:**
- ❌ Need to rebuild image when API URL changes
- ❌ Requires GitHub token to push

---

### Option 2: Build from Source in Dokploy (More Flexible)

Change the compose file to build from source instead of using a pre-built image.

**Updated Compose File:**

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: https://api.lawscoutai.com
    container_name: lawscout-frontend
    environment:
      - NODE_ENV=production
      - PORT=3000
    networks:
      - dokploy-network
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

networks:
  dokploy-network:
    external: true
```

**In Dokploy:**

1. **Update the Compose File:**
   - Replace the compose file content with the above
   - Make sure the repository is connected and code is available

2. **Configure Build:**
   - Dokploy should detect the `build:` section
   - It will build from source on each deploy

**Pros:**
- ✅ Always uses latest code
- ✅ Build arguments work correctly
- ✅ No need to push to registry
- ✅ More flexible for changes

**Cons:**
- ❌ Slower deployments (builds every time)
- ❌ Requires build tools on Dokploy server

---

### Option 3: Use Environment Variable with Build (Hybrid)

Keep using the image but set build arg via environment variable in compose.

**Updated Compose File:**

```yaml
version: '3.8'

services:
  frontend:
    image: ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
    container_name: lawscout-frontend
    environment:
      - NODE_ENV=production
      - PORT=3000
      # Note: NEXT_PUBLIC_API_URL won't work here - it's already baked into the image
    networks:
      - dokploy-network
    restart: unless-stopped
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
      - "traefik.http.routers.frontend.entrypoints=websecure"
      - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"

networks:
  dokploy-network:
    external: true
```

**Then rebuild the image once with correct API URL** (see Option 1).

---

## Recommended Approach

**For your situation, I recommend Option 1:**

1. Rebuild the image with correct API URL using the deploy script
2. Keep using the pre-built image in compose
3. Add Traefik labels to the compose file
4. Redeploy

This gives you:
- ✅ Fast deployments (pre-built image)
- ✅ Correct API URL (baked into build)
- ✅ Works with your current setup

---

## Quick Fix Steps

1. **Rebuild Image:**
   ```bash
   export GITHUB_TOKEN=your_token
   ./scripts/deploy.sh
   ```

2. **Update Compose File in Dokploy:**
   - Remove `NEXT_PUBLIC_API_URL` from environment (it's already in the image)
   - Add Traefik labels (if not already there)
   - Keep using `image: ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`

3. **Redeploy:**
   - Dokploy will pull the new image
   - Restart the container

---

## Verify It's Working

After redeploying:

1. **Check Logs:**
   - Should see "Ready on http://localhost:3000"

2. **Test in Browser:**
   - Visit `https://lawscoutai.com`
   - Open browser console
   - Should see: `🔍 Frontend API URL: https://api.lawscoutai.com`

3. **Test API Connection:**
   - Try login/register
   - Should connect to `https://api.lawscoutai.com`

---

## Important Notes

- **Environment variables** for `NEXT_PUBLIC_*` don't work at runtime
- They must be set as **build arguments** during `docker build`
- Once baked into the image, they can't be changed without rebuilding
- The compose file's `environment:` section won't affect `NEXT_PUBLIC_*` vars

---

**Last Updated:** December 2025

