# Cloudflare CDN Setup for LawScout AI

## Why Cloudflare?

Cloudflare CDN provides significant performance improvements:
- **Edge Caching**: Responses cached at 300+ global locations
- **Faster Routing**: Optimized network paths
- **Compression**: Automatic gzip/brotli compression
- **DDoS Protection**: Built-in security
- **HTTP/2 & HTTP/3**: Modern protocol support

The monolithic Streamlit version benefits from Cloudflare, which is why it feels faster.

## Setup Steps

### 1. Add Your Domain to Cloudflare

**Important:** You're proxying `lawscout-frontend-latest.onrender.com` to `lawscoutai.com`

1. Your domain in Cloudflare: `lawscoutai.com` (the public-facing domain)
2. Cloudflare proxies requests to: `lawscout-frontend-latest.onrender.com` (Render origin)
3. DNS records should point `lawscoutai.com` → Cloudflare → Render

**Current Setup:**
- Public domain: `lawscoutai.com` (what users access)
- Origin: `lawscout-frontend-latest.onrender.com` (where Cloudflare proxies to)

### 2. Configure Cloudflare for Frontend (Next.js)

**Page Rules (Free Tier - 3 rules available):**

Rule 1: Cache Static Assets (Highest Priority)
```
URL Pattern: *lawscoutai.com/_next/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 year (31536000 seconds)
  - Browser Cache TTL: 1 year
```

Rule 2: Cache HTML Pages
```
URL Pattern: *lawscoutai.com/*
Settings:
  - Cache Level: Standard
  - Edge Cache TTL: 1 hour (3600 seconds)
  - Browser Cache TTL: Respect Existing Headers
```

**Important:** Use `lawscoutai.com` in Page Rules (the public domain), NOT `lawscout-frontend-latest.onrender.com`!

**Note:** If you only have 1 free Page Rule, use Rule 1 for static assets (most important).

### 3. Configure Cloudflare for Backend (FastAPI)

**Page Rules (Use remaining free rules if available):**

**Backend Caching (No Page Rules needed):**

The backend already sends proper `Cache-Control` headers:
- `Cache-Control: public, max-age=300, s-maxage=1800`
- `ETag` headers for conditional requests

Cloudflare's free tier will automatically respect these headers when proxying requests. No Page Rules needed for the backend!

**Important:** Make sure your backend CORS includes `lawscoutai.com` (see backend configuration below).

### 4. Enable Cloudflare Features (All Free!)

**Speed Tab (Free Tier):**
- ✅ Auto Minify: JavaScript, CSS, HTML (FREE)
- ✅ Brotli: Enabled (FREE)
- ✅ HTTP/2: Enabled (FREE)
- ✅ HTTP/3 (with QUIC): Enabled (FREE)
- ✅ 0-RTT Connection Resumption: Enabled (FREE)

**Caching Tab (Free Tier):**
- Caching Level: Standard (FREE)
- Browser Cache TTL: Respect Existing Headers (FREE)
- Always Online: Enabled (FREE) - Only works if origin is down

**Note:** All these features are available on the FREE plan!

**Network Tab:**
- HTTP/2: Enabled
- HTTP/3 (with QUIC): Enabled
- 0-RTT Connection Resumption: Enabled
- IP Geolocation: Enabled

### 5. Configure Backend CORS for Cloudflare Domain

**Critical:** Your backend must allow requests from `lawscoutai.com` (the Cloudflare-proxied domain).

Update `backend/main.py` CORS settings:
```python
allow_origins=[
    "https://lawscoutai.com",                    # ✅ Cloudflare-proxied domain (REQUIRED)
    "https://lawscout-frontend-latest.onrender.com",  # Render origin (for direct access)
    "https://lawscout-backend-latest.onrender.com",   # Backend origin
    "http://localhost:3000",                     # Local dev
]
```

**Why:** When users access `lawscoutai.com`, Cloudflare proxies to Render, but the browser sees the request as coming from `lawscoutai.com`, so CORS must allow that domain.

### 6. DNS Configuration in Cloudflare

**For `lawscoutai.com`:**
1. DNS Record Type: `CNAME` or `A` (depending on Render setup)
2. Name: `@` (root domain) or `www` (if using www subdomain)
3. Target: `lawscout-frontend-latest.onrender.com` (Render origin)
4. Proxy Status: ✅ Proxied (orange cloud icon) - **This is critical!**

**Verify:**
- Orange cloud = Proxied through Cloudflare ✅
- Gray cloud = DNS only (no CDN) ❌

### 7. Verify Caching

Test cache headers:
```bash
# Check frontend static assets (should be cached)
curl -I https://lawscoutai.com/_next/static/some-file.js

# Check backend API (should respect Cache-Control)
curl -I https://lawscout-backend-latest.onrender.com/api/v1/search \
  -H "Accept-Encoding: gzip" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# Look for:
# - Cache-Control header (from backend)
# - ETag header (from backend)
# - CF-Cache-Status: HIT (if cached by Cloudflare)
# - CF-RAY header (confirms request went through Cloudflare)
```

## Expected Performance Gains

With Cloudflare CDN:
- **First Request**: Same as before (~9-10s)
- **Cached Requests**: <100ms (served from edge)
- **Network Transfer**: 60-80% reduction (compression)
- **Global Latency**: 30-50% reduction (edge locations)

## Cache Invalidation

If you need to clear cache:
1. Cloudflare Dashboard → Caching → Purge Everything
2. Or use API: `POST /purge_cache` with API token

## Monitoring

Check cache hit rate:
- Cloudflare Dashboard → Analytics → Caching
- Look for "Cache Hit Ratio" (aim for >80%)

## Troubleshooting

**Cache not working?**
- Check Cache-Control headers in response
- Verify Page Rules are active
- Check CF-Cache-Status header

**CORS errors?**
- Ensure Cloudflare domain is in backend CORS allow_origins
- Check if Cloudflare is modifying headers

**Slow responses?**
- Check Cloudflare Analytics for cache hit ratio
- Verify compression is enabled
- Check if requests are reaching origin (should be cached)

## Cost

✅ **Everything in this guide uses the FREE plan!**

Cloudflare Free Plan includes:
- ✅ Unlimited bandwidth
- ✅ DDoS protection
- ✅ Global CDN with 200+ edge locations
- ✅ SSL/TLS certificates
- ✅ Basic analytics
- ✅ Auto Minify (JS/CSS/HTML)
- ✅ Brotli compression
- ✅ HTTP/2 and HTTP/3
- ✅ 3 Page Rules (enough for basic setup)

**No paid features required!** The backend's `Cache-Control` headers work perfectly with Cloudflare's free tier caching.

## Free Tier Limitations (Not a Problem)

- **3 Page Rules max** - Use 1-2 for static assets, backend will use default caching
- **Basic analytics** - Still shows cache hit ratio and performance
- **No Cache Rules** - Not needed! Our backend headers work with default caching

All optimizations in this guide work perfectly on the free plan!

