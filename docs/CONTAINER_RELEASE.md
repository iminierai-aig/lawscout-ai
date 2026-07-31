# Container Release and Dokploy Deployment

This is the canonical production release process for LawScout AI.

## Production artifacts

LawScout AI deploys two prebuilt images from GitHub Container Registry (GHCR):

- Backend: `ghcr.io/iminierai-aig/lawscout-ai-backend:<version>`
- Frontend: `ghcr.io/iminierai-aig/lawscout-ai-frontend:<version>`

Dokploy must pull these images. It should not build the production services from repository source.

Use immutable version tags such as `v2.1.3`. The workflow also publishes `sha-<commit>` and `latest`, but production should point at the version tag so a deployment is reproducible and rollback is immediate.

## 1. Validate the release

Before publishing:

1. Merge the intended changes into `master`.
2. Confirm the `CI` workflow passes.
3. Choose the next unused semantic version, for example `v2.1.3`.

Never reuse a version tag for different code.

## 2. Publish both images

### Git tag release

```bash
git checkout master
git pull --ff-only origin master
git tag -a v2.1.3 -m "LawScout AI v2.1.3"
git push origin v2.1.3
```

Pushing a `v*` tag starts `.github/workflows/publish-images.yml`.

### Manual release

In GitHub:

1. Open **Actions → Publish production images**.
2. Select **Run workflow** on `master`.
3. Enter an unused tag such as `v2.1.3`.
4. Wait for both `backend` and `frontend` jobs to pass.

The workflow publishes:

```text
ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.3
ghcr.io/iminierai-aig/lawscout-ai-backend:sha-<commit>
ghcr.io/iminierai-aig/lawscout-ai-backend:latest

ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.3
ghcr.io/iminierai-aig/lawscout-ai-frontend:sha-<commit>
ghcr.io/iminierai-aig/lawscout-ai-frontend:latest
```

The frontend image is built with `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com` because Next.js embeds this value at build time.

## 3. Configure Dokploy

### Backend service

Set the image to:

```text
ghcr.io/iminierai-aig/lawscout-ai-backend:v2.1.3
```

Container port: `8000`

Required environment variables:

```text
QDRANT_URL=...
QDRANT_API_KEY=...
GEMINI_API_KEY=...
JWT_SECRET_KEY=...
SESSION_SECRET=...
FRONTEND_URL=https://lawscoutai.com
BACKEND_URL=https://api.lawscoutai.com
ADMIN_EMAILS=...
PORT=8000
```

Persist `/app/data` with a Dokploy volume. The default SQLite database is `/app/data/users.db`; deploying without this volume can lose account and search-history data.

Optional variables:

```text
DATABASE_URL=sqlite:////app/data/users.db
RATELIMIT_STORAGE_URI=redis://...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

When running multiple backend workers, Redis-backed rate limiting is recommended because the default limiter store is process-local.

Health check: `GET /health`

### Frontend service

Set the image to:

```text
ghcr.io/iminierai-aig/lawscout-ai-frontend:v2.1.3
```

Container port: `3000`

Environment variables:

```text
NODE_ENV=production
PORT=3000
```

Changing `NEXT_PUBLIC_API_URL` at runtime does not change the compiled frontend. Publish a new frontend image with the desired build argument instead.

### Private GHCR packages

If the images are private, configure Dokploy registry credentials for `ghcr.io` with a GitHub token that can read packages. Do not place this token in the application environment.

## 4. Deploy in order

1. Update and deploy the backend version tag.
2. Wait for the backend health check to pass.
3. Update and deploy the frontend using the same version tag.
4. Keep the previous version tag available for rollback.

## 5. Verify production

```bash
curl --fail https://api.lawscoutai.com/health
curl --fail https://api.lawscoutai.com/api/auth/health
curl --fail https://lawscoutai.com/
```

Then verify in a browser:

1. Register or sign in.
2. Run a search.
3. Confirm sources and citations render.
4. Confirm the remaining-search count decreases exactly once.
5. Confirm unauthenticated search requests receive `401`.

Do not use real client-sensitive queries for deployment testing.

## Rollback

In Dokploy, set both services back to their previous immutable tags and redeploy. Deploy the backend first, then the frontend.

Do not roll back the `/app/data` volume unless a database restoration is explicitly required.
