# Updating Existing Dokploy Frontend Service

## Option 1: Update Existing Service (Recommended)

If you already have a frontend service deployed in Dokploy, you can update it:

### Steps:

1. **Go to Your Existing Frontend Service**
   - Open Dokploy dashboard
   - Find your existing frontend application
   - Click on it to open settings

2. **Update Repository Settings** (if needed)
   - Verify **Dockerfile Path**: `frontend/Dockerfile`
   - Verify **Docker Context**: `frontend/`
   - Verify **Branch**: Your current branch (e.g., `feature/option-c-microservices`)

3. **Update Build Arguments** (CRITICAL!)
   - Go to **Build Arguments** section
   - Add/Update: `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com`
   - **⚠️ This is required** - Next.js bakes this into the build

4. **Update Environment Variables**
   - Go to **Environment Variables** section
   - Add/Update:
     ```
     NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
     NODE_ENV=production
     PORT=3000
     ```

5. **Update Traefik Labels** (if routing changed)
   - Go to **Labels** or **Traefik** section
   - Ensure these labels are set:
     ```
     traefik.enable = true
     traefik.http.routers.frontend.rule = Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)
     traefik.http.routers.frontend.entrypoints = websecure
     traefik.http.routers.frontend.tls.certresolver = letsencrypt
     traefik.http.services.frontend.loadbalancer.server.port = 3000
     ```

6. **Redeploy**
   - Click **"Redeploy"** or **"Deploy"** button
   - Dokploy will:
     - Pull latest code from GitHub
     - Rebuild with new build arguments
     - Restart the container

---

## Option 2: Delete and Recreate (If Update Fails)

If updating the existing service doesn't work or you want a fresh start:

### Steps:

1. **Stop the Existing Service**
   - Go to your frontend service in Dokploy
   - Click **"Stop"** or **"Delete"**
   - Confirm deletion

2. **Create New Service**
   - Follow the steps in `DOKPLOY_QUICK_START.md`
   - Use the same name or a new name

3. **Verify Old Service is Removed**
   - Check that old container is stopped
   - Verify Traefik routing points to new service

---

## Option 3: Keep Both (Testing)

If you want to test the new deployment alongside the old one:

1. **Create New Service with Different Name**
   - Name: `lawscout-frontend-v2` or `lawscout-frontend-new`
   - Use different port (e.g., 3001) temporarily
   - Test it works

2. **Switch Traefik Routing**
   - Update Traefik labels to point to new service
   - Or use a test subdomain: `test.lawscoutai.com`

3. **Delete Old Service**
   - Once new service is verified
   - Delete the old one
   - Rename new service if needed

---

## What to Check Before Updating

### Current Service Configuration

Check your existing service has:

- ✅ **Correct Dockerfile path**: `frontend/Dockerfile`
- ✅ **Correct Docker context**: `frontend/`
- ✅ **Build argument**: `NEXT_PUBLIC_API_URL` (may be missing!)
- ✅ **Environment variables**: All required vars set
- ✅ **Traefik labels**: Routing configured correctly
- ✅ **Port**: `3000` exposed

### Common Issues with Existing Services

**Issue: Old API URL**
- If service was deployed before migration to Hostinger VPS
- Old URL might be: `https://lawscout-backend-latest.onrender.com`
- **Fix**: Update `NEXT_PUBLIC_API_URL` build argument and redeploy

**Issue: Missing Build Argument**
- `NEXT_PUBLIC_API_URL` might only be set as env var
- **Fix**: Add it as build argument (required for Next.js)

**Issue: Wrong Docker Context**
- Dockerfile might be looking in wrong directory
- **Fix**: Set Docker context to `frontend/`

---

## Recommended Approach

**For most cases, use Option 1 (Update Existing):**

1. ✅ Faster - no downtime
2. ✅ Preserves configuration
3. ✅ Just updates what's needed
4. ✅ Less risk

**Only use Option 2 (Delete/Recreate) if:**
- Service is completely misconfigured
- Update keeps failing
- You want a clean slate

---

## Verification After Update

After updating/redeploying:

1. **Check Logs**
   ```
   Should see: "Ready on http://localhost:3000"
   No errors about missing modules
   ```

2. **Test Frontend**
   ```bash
   curl https://lawscoutai.com
   # Should return HTML
   ```

3. **Check Browser Console**
   - Visit `https://lawscoutai.com`
   - Open DevTools → Console
   - Should see: `🔍 Frontend API URL: https://api.lawscoutai.com`

4. **Test Functionality**
   - Try login/register
   - Try search
   - Check auth is working

---

## Quick Update Checklist

- [ ] Open existing frontend service in Dokploy
- [ ] Verify Dockerfile path: `frontend/Dockerfile`
- [ ] Verify Docker context: `frontend/`
- [ ] Add build argument: `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com`
- [ ] Update environment variables
- [ ] Verify Traefik labels
- [ ] Click "Redeploy"
- [ ] Check logs for success
- [ ] Test frontend in browser
- [ ] Verify API URL in console

---

**Last Updated:** December 2024

