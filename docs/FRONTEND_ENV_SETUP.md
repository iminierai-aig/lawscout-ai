# Frontend Environment Variables Setup

## Required Environment Variables

### Production (Hostinger VPS)

**File:** `.env.production` or set in Dokploy/Docker

```bash
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
NODE_ENV=production
PORT=3000
```

### Development (Local)

**File:** `.env.local` (not committed to git)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Docker Build Configuration

### Using Dockerfile

The Dockerfile accepts `NEXT_PUBLIC_API_URL` as a build argument:

```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://api.lawscoutai.com \
  -t lawscout-frontend:latest \
  ./frontend
```

### Using Docker Compose

```yaml
services:
  frontend:
    build:
      context: ./frontend
      args:
        NEXT_PUBLIC_API_URL: https://api.lawscoutai.com
    environment:
      - NODE_ENV=production
      - PORT=3000
```

## Dokploy Configuration

1. Go to your Dokploy project
2. Navigate to **Environment Variables**
3. Add:
   - `NEXT_PUBLIC_API_URL` = `https://api.lawscoutai.com`
   - `NODE_ENV` = `production`
   - `PORT` = `3000`

## Important Notes

### Next.js Public Variables

- Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser
- They are **baked into the build** at build time
- Changing them requires **rebuilding** the Docker image
- They are **not** available at runtime

### Build-Time vs Runtime

```typescript
// ✅ This works (build-time)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com'

// ❌ This won't work (runtime - not available in browser)
const SECRET = process.env.SECRET_KEY  // undefined in browser
```

### Current Default Values

The code has fallback defaults:
- `frontend/src/lib/api.ts`: `https://api.lawscoutai.com`
- `frontend/src/app/page.tsx`: `https://api.lawscoutai.com`
- `frontend/next.config.js`: `https://api.lawscoutai.com`

## Verification

After setting environment variables, verify they're being used:

1. **Check build logs** - Should show the API URL being used
2. **Browser console** - The page logs the API URL on load
3. **Network tab** - API requests should go to the configured URL

## Troubleshooting

### API requests going to wrong URL

1. Rebuild the Docker image with correct `NEXT_PUBLIC_API_URL`
2. Clear browser cache
3. Check browser console for logged API URL

### Environment variable not working

1. Ensure variable starts with `NEXT_PUBLIC_`
2. Rebuild the application (not just restart)
3. Check that variable is set before `npm run build`

---

**Last Updated:** December 2024

