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

1. Sign up at [cloudflare.com](https://www.cloudflare.com)
2. Add your domain (e.g., `lawscout-frontend-latest.onrender.com`)
3. Update DNS records to point to Cloudflare

### 2. Configure Cloudflare for Frontend (Next.js)

**Cache Rules:**
- **Static Assets** (`.next/static/*`): Cache for 1 year
- **HTML Pages**: Cache for 1 hour
- **API Routes**: Don't cache (pass through)

**Page Rules:**
```
URL Pattern: *lawscout-frontend-latest.onrender.com/_next/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 year
  - Browser Cache TTL: 1 year
```

### 3. Configure Cloudflare for Backend (FastAPI)

**Cache Rules:**
- **API Responses**: Cache based on Cache-Control headers
- **Health Endpoint**: Don't cache

**Page Rules:**
```
URL Pattern: *lawscout-backend-latest.onrender.com/api/v1/search*
Settings:
  - Cache Level: Respect Existing Headers
  - Edge Cache TTL: Use origin's Cache-Control
  - Browser Cache TTL: Use origin's Cache-Control
```

**Transform Rules (Optional):**
Add response headers for better caching:
```
Header: Cache-Control
Value: public, max-age=300, s-maxage=1800
```

### 4. Enable Cloudflare Features

**Speed Tab:**
- ✅ Auto Minify: JavaScript, CSS, HTML
- ✅ Brotli: Enabled
- ✅ HTTP/2: Enabled
- ✅ HTTP/3 (with QUIC): Enabled
- ✅ 0-RTT Connection Resumption: Enabled

**Caching Tab:**
- Caching Level: Standard
- Browser Cache TTL: Respect Existing Headers
- Always Online: Enabled

**Network Tab:**
- HTTP/2: Enabled
- HTTP/3 (with QUIC): Enabled
- 0-RTT Connection Resumption: Enabled
- IP Geolocation: Enabled

### 5. Configure Render.com with Cloudflare

**For Frontend:**
1. In Render Dashboard → Settings → Custom Domain
2. Add your Cloudflare-managed domain
3. Update DNS in Cloudflare to point to Render

**For Backend:**
1. Same process as frontend
2. Ensure CORS allows your Cloudflare domain

### 6. Verify Caching

Test cache headers:
```bash
# Check if responses are cached
curl -I https://your-domain.com/api/v1/search \
  -H "Accept-Encoding: gzip" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# Look for:
# - Cache-Control header
# - ETag header
# - CF-Cache-Status: HIT (if cached)
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

Cloudflare Free Plan includes:
- Unlimited bandwidth
- DDoS protection
- Global CDN
- SSL/TLS certificates
- Basic analytics

This is sufficient for most use cases!

