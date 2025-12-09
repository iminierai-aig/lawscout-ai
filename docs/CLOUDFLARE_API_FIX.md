# Fix: API Requests Failing Through Cloudflare Proxy

## Problem

- ✅ `https://lawscout-frontend-latest.onrender.com` - **WORKS** (direct Render access)
- ❌ `https://lawscoutai.com` - **FAILS** (Cloudflare-proxied domain)

This indicates Cloudflare is blocking or modifying API requests from the proxied domain.

## Root Cause

When users access `lawscoutai.com`:
1. Browser makes request to `lawscoutai.com` (Cloudflare edge)
2. Frontend JavaScript tries to call backend at `https://lawscout-backend-latest.onrender.com`
3. **Cloudflare may be blocking this cross-origin request** or modifying headers
4. CORS preflight (OPTIONS) might be failing

## Solution 1: Cloudflare Page Rule for API Requests (Recommended)

Create a Page Rule in Cloudflare to allow API requests:

**Rule: Allow API Requests**
```
URL Pattern: lawscoutai.com/api/*
Settings:
  - Cache Level: Bypass
  - Security Level: Medium (or Low if needed)
  - Disable Apps: Off
  - Disable Performance: Off
```

**Why this works:**
- Bypasses caching for API requests (they're dynamic)
- Allows the requests to pass through Cloudflare to your backend
- Doesn't interfere with static asset caching

## Solution 2: Proxy API Through Cloudflare (Alternative)

If you want all API requests to go through Cloudflare:

1. **Set up a subdomain for API:**
   - Create `api.lawscoutai.com` CNAME pointing to `lawscout-backend-latest.onrender.com`
   - Enable Cloudflare proxy (orange cloud) for this subdomain

2. **Update frontend to use proxied API:**
   - Rebuild frontend with `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com`
   - This routes all API requests through Cloudflare

3. **Update backend CORS:**
   ```python
   allow_origins=[
       "https://lawscoutai.com",
       "https://api.lawscoutai.com",  # Add this
       # ... other origins
   ]
   ```

## Solution 3: Check Cloudflare Security Settings

1. **Go to Cloudflare Dashboard → Security → WAF**
2. **Check if any rules are blocking requests:**
   - Look for blocked requests in "Security Events"
   - Check if "Browser Integrity Check" is too strict
   - Verify "Challenge Passage" settings

3. **Temporarily disable security features to test:**
   - Security Level: Medium or Low
   - Browser Integrity Check: Off (temporarily)
   - If it works, gradually re-enable features

## Solution 4: Verify CORS Headers

Check if Cloudflare is modifying CORS headers:

```bash
# Test from lawscoutai.com origin
curl -X OPTIONS https://lawscout-backend-latest.onrender.com/api/v1/search \
  -H "Origin: https://lawscoutai.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  -v

# Look for:
# - Access-Control-Allow-Origin: https://lawscoutai.com
# - Access-Control-Allow-Methods: POST
```

If headers are missing or wrong, the backend CORS needs updating.

## Solution 5: Use Cloudflare Workers (Advanced)

Create a Cloudflare Worker to proxy API requests:

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Proxy API requests to backend
  if (request.url.includes('/api/')) {
    const backendUrl = 'https://lawscout-backend-latest.onrender.com'
    const url = new URL(request.url)
    const backendRequest = new Request(
      `${backendUrl}${url.pathname}${url.search}`,
      {
        method: request.method,
        headers: request.headers,
        body: request.body
      }
    )
    return fetch(backendRequest)
  }
  // Otherwise, fetch from origin
  return fetch(request)
}
```

## Quick Diagnostic Steps

1. **Open browser console on `lawscoutai.com`**
2. **Look for the API URL log:**
   ```
   🔍 Frontend API URL: https://lawscout-backend-latest.onrender.com
   ```
3. **Check Network tab:**
   - Find the failed `/api/v1/search` request
   - Check the **Request Headers** - is `Origin: https://lawscoutai.com`?
   - Check the **Response Headers** - are CORS headers present?
   - What's the error? (CORS, 403, 502, etc.)

4. **Test backend directly:**
   ```bash
   curl -X POST https://lawscout-backend-latest.onrender.com/api/v1/search \
     -H "Origin: https://lawscoutai.com" \
     -H "Content-Type: application/json" \
     -d '{"query":"test","collection":"both","limit":5}'
   ```

## Most Likely Fix

**Start with Solution 1 (Page Rule)** - it's the simplest and most effective:

1. Go to Cloudflare Dashboard → Rules → Page Rules
2. Create new rule:
   - URL: `*lawscoutai.com/api/*`
   - Settings: Cache Level = Bypass
3. Save and test

This allows API requests to bypass Cloudflare's caching and security checks while still benefiting from CDN for static assets.

## Verification

After applying the fix:
1. Clear browser cache
2. Visit `https://lawscoutai.com`
3. Open browser console (F12)
4. Make a search request
5. Check Network tab - API request should succeed
6. Check console for: `🔍 Frontend API URL: https://lawscout-backend-latest.onrender.com`

