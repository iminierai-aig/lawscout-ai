# Changelog

All notable production changes to LawScout AI are recorded here. Production releases use immutable GHCR image tags.

## Unreleased

## v2.1.6 - 2026-07-31

### Changed

- Migrated frontend linting from deprecated `next lint` to the ESLint CLI.
- Resolved the existing frontend lint findings and added warning-free linting to CI.
- Upgraded GitHub and Docker Actions to Node 24-compatible major versions.

### Deployment

- Published and deployed backend and frontend images as `v2.1.6`.
- Reverified backend health, authentication health, frontend availability, stale-cookie routing, and unauthenticated search rejection in production.

## v2.1.5 - 2026-07-31

### Security

- Upgraded Next.js from 14.2.35 to 15.5.22.
- Upgraded Axios to 1.19.0 and patched vulnerable PostCSS, Sharp, and Picomatch dependencies.
- Reduced the frontend npm audit result from six findings to zero.
- Added a CI dependency audit that rejects high-severity findings.

### Tests

- Added production routing checks proving stale authentication cookies cannot block `/login` or `/register`.
- Retained the unauthenticated redirect for protected frontend routes.

### Deployment

- Published backend and frontend images as `v2.1.5`.
- Verified backend health, authentication health, frontend availability, stale-cookie routing, and unauthenticated search rejection in production.

## v2.1.4 - 2026-07-31

### Fixed

- Cleared invalid authentication cookies when token validation fails.
- Stopped middleware from treating an unvalidated cookie as proof of authentication.
- Fixed the login and registration buttons appearing inert because stale cookies redirected both routes to the homepage.

### Deployment

- Published `v2.1.4`; the frontend hotfix was deployed after CI and container validation passed.

## v2.1.3 - 2026-07-31

### Security

- Required authentication for legal search requests.
- Enforced search quotas atomically on the backend and refunded failed searches.
- Added authorization to administrative endpoints and fail-closed JWT secret handling.
- Added search and authentication rate limiting.
- Prevented legal queries and results from being publicly cached.

### Fixed

- Prevented duplicate frontend usage tracking; one successful search now decrements usage exactly once.
- Fixed source metadata and citation preservation.
- Fixed court metadata initialization and added request validation.
- Added configurable `DATABASE_URL` support.

### Delivery

- Added backend regression tests and frontend/backend CI builds.
- Added immutable GHCR image publishing for separate Dokploy services.
- Documented the canonical container release and rollback process.
