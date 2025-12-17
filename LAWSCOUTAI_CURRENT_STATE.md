# LawScout AI - Current System State

**Last Updated:** December 2025  
**Version:** 2.1.1  
**Status:** ✅ Production - Fully Operational

---

## 🌐 Public Access

- **Primary Domain:** `https://www.lawscoutai.com` (Cloudflare-proxied)
- **Alternative Domain:** `https://lawscoutai.com` (also works)
- **Status:** Fully functional, CORS configured correctly

---

## 🏗️ Architecture Overview

LawScout AI uses a **microservices architecture** with separate frontend and backend services:

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                            │
│              (https://www.lawscoutai.com)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare CDN                            │
│  • Edge caching (300+ locations)                            │
│  • DDoS protection                                           │
│  • Automatic compression (gzip/brotli)                       │
│  • HTTP/2 & HTTP/3 support                                   │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
                ▼                       ▼
    ┌───────────────────┐   ┌───────────────────┐
    │   Frontend        │   │   Backend          │
    │   (Next.js)       │   │   (FastAPI)        │
    │                   │   │                   │
    │ Render.com        │   │ Render.com        │
    │ Port: 3000        │   │ Port: 8000        │
    └─────────┬─────────┘   └─────────┬─────────┘
              │                       │
              │                       ▼
              │           ┌───────────────────────┐
              │           │   RAG Engine          │
              │           │   (LegalRAGEngine)   │
              │           └───────────┬───────────┘
              │                       │
              │                       ├───▶ Qdrant Cloud
              │                       │     (Vector Database)
              │                       │     171,813 vectors
              │                       │
              │                       └───▶ Google Gemini API
              │                             (gemini-2.5-flash)
              │                             Answer Generation
              │
              └───────────────────────────▶ API Calls
                                            POST /api/v1/search
```

---

## 🎨 Frontend (Next.js)

### Technology Stack
- **Framework:** Next.js 14+ (React)
- **Styling:** Tailwind CSS (Harvey.ai-inspired design)
- **HTTP Client:** Axios (with connection pooling)
- **State Management:** React Hooks (useState, useEffect)
- **Storage:** localStorage (query history)

### Deployment
- **Platform:** Render.com
- **Service Name:** `lawscout-frontend-latest`
- **URL:** `https://lawscout-frontend-latest.onrender.com`
- **Docker Image:** `ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`
- **Port:** 3000
- **Build:** Docker container with Next.js production build

### Key Features
- ✅ Modern, responsive UI (Harvey.ai-inspired design)
- ✅ Sidebar with query history and settings
- ✅ Real-time search with loading states
- ✅ Source document expansion/collapse
- ✅ Export results to Markdown
- ✅ Query history (stored in localStorage)
- ✅ Advanced search filters (hybrid search, reranking, citations)
- ✅ Collection selection (both, contracts, cases)

### API Configuration
- **Backend URL:** Set via `NEXT_PUBLIC_API_URL` environment variable
- **Default:** `https://lawscout-backend-latest.onrender.com`
- **Endpoint:** `/api/v1/search`
- **Timeout:** 60 seconds
- **Headers:** 
  - `Content-Type: application/json`
  - `Accept: application/json`
  - (Note: `Accept-Encoding` removed - browsers handle automatically)

### CORS Configuration
- Frontend makes requests from `https://www.lawscoutai.com`
- Backend must allow this origin (✅ configured)

---

## ⚙️ Backend (FastAPI)

### Technology Stack
- **Framework:** FastAPI (Python 3.11)
- **Server:** Gunicorn with Uvicorn workers (2 workers)
- **Middleware:** 
  - CORS (Cross-Origin Resource Sharing)
  - GZip compression
- **Logging:** File + console logging

### Deployment
- **Platform:** Render.com
- **Service Name:** `lawscout-backend-latest`
- **URL:** `https://lawscout-backend-latest.onrender.com`
- **Docker Image:** `ghcr.io/iminierai-aig/lawscout-ai-backend:latest`
- **Port:** 8000
- **Workers:** 2 (Gunicorn + Uvicorn)

### API Endpoints

#### `POST /api/v1/search`
Main search endpoint for legal queries.

**Request:**
```json
{
  "query": "What are termination clauses in software licenses?",
  "collection": "both",  // "both", "contracts", or "cases"
  "limit": 5,
  "use_hybrid": true,
  "use_reranking": true,
  "extract_citations": true
}
```

**Response:**
```json
{
  "answer": "AI-generated answer with citations...",
  "sources": [
    {
      "content": "Document text...",
      "score": 0.85,
      "metadata": {
        "title": "Case Name or Contract Title",
        "collection": "cases",
        "court": "Supreme Court",
        "date": "2023-01-15",
        "citation": "123 U.S. 456",
        "url": "https://www.courtlistener.com/..."
      }
    }
  ],
  "metadata": {
    "total_searched": 171813,
    "query_time": 3.45,
    "collection": "both"
  }
}
```

#### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "rag_engine": "initialized",
  "memory_mb": 1234.56,
  "memory_warning": false
}
```

### CORS Configuration
Backend allows requests from:
- ✅ `https://lawscoutai.com`
- ✅ `https://www.lawscoutai.com` (recently added - fixes CORS issues)
- ✅ `https://lawscout-frontend-latest.onrender.com`
- ✅ `https://lawscout-backend-latest.onrender.com`
- ✅ `http://localhost:3000` (local dev)
- ✅ `http://localhost:8501` (local Streamlit dev)

### Performance Optimizations
- ✅ **Query Caching:** LRU cache (100 entries) for repeated queries
- ✅ **Thread Pool:** Dedicated executor (4 workers) for RAG operations
- ✅ **Response Compression:** GZip middleware (reduces transfer size)
- ✅ **CDN Caching:** Cache-Control headers for Cloudflare
  - Browser cache: 5 minutes
  - CDN cache: 30 minutes
  - Cache HIT responses: 1 hour

### Logging
- **File:** `backend/logs/backend.log`
- **Console:** Also logs to stdout/stderr
- **Format:** `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- **Level:** INFO

---

## 🧠 RAG System (LegalRAGEngine)

### Components

#### 1. **Hybrid Search Engine**
- **Semantic Search:** Vector similarity using `all-MiniLM-L6-v2` embeddings
- **Keyword Search:** BM25 algorithm for exact matches
- **Combination:** Weighted fusion of both results

#### 2. **Reranking**
- **Model:** Cross-encoder for improved relevance
- **Process:** Reranks top results from hybrid search

#### 3. **Citation Extraction**
- **Tool:** Automatic legal citation detection
- **Links:** CourtListener URLs for case law
- **Format:** Standard legal citation format

#### 4. **Answer Generation**
- **Model:** Google Gemini 2.5 Flash
- **Context:** Top relevant documents from search
- **Output:** Natural language answer with citations

### Data Sources
- **Case Law:** CourtListener (federal cases)
- **Contracts:** CUAD Dataset (commercial contracts)
- **Total Documents:** 240,633
- **Total Chunks:** 171,813
- **Vector Dimensions:** 384 (all-MiniLM-L6-v2)

### Vector Database
- **Platform:** Qdrant Cloud
- **Collections:** 
  - `legal_cases` (case law)
  - `legal_contracts` (contracts)
- **Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Index:** HNSW (Hierarchical Navigable Small World)

---

## ☁️ Cloudflare CDN Configuration

### DNS Setup
- **Domain:** `lawscoutai.com` → Cloudflare → Render
- **Frontend:** `lawscoutai.com` → `lawscout-frontend-latest.onrender.com`
- **Backend:** Direct access to `lawscout-backend-latest.onrender.com`

### Page Rules (Free Tier)
1. **Static Assets Caching:**
   - Pattern: `*lawscoutai.com/_next/static/*`
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 year

2. **HTML Pages:**
   - Pattern: `*lawscoutai.com/*`
   - Cache Level: Standard
   - Edge Cache TTL: 1 hour

### Enabled Features (All Free)
- ✅ Auto Minify (JavaScript, CSS, HTML)
- ✅ Brotli Compression
- ✅ HTTP/2
- ✅ HTTP/3 (with QUIC)
- ✅ 0-RTT Connection Resumption
- ✅ DDoS Protection

---

## 🚀 Deployment Process

### Docker Images
Both services are containerized and stored in GitHub Container Registry:

- **Backend:** `ghcr.io/iminierai-aig/lawscout-ai-backend:latest`
- **Frontend:** `ghcr.io/iminierai-aig/lawscout-ai-frontend:latest`

### Deployment Script
```bash
./scripts/deploy.sh
```

This script:
1. Builds backend Docker image
2. Builds frontend Docker image (with `NEXT_PUBLIC_API_URL` build arg)
3. Pushes both to GitHub Container Registry
4. Tags as `latest` for Render to pull

### Render Configuration
- **Auto-Deploy:** Enabled (pulls `latest` tag)
- **Manual Deploy:** Available via Render dashboard
- **Environment Variables:** Set in Render dashboard
- **Health Checks:** `/health` endpoint for backend

---

## 🔧 Recent Fixes (December 2024)

### CORS Configuration
**Issue:** Requests from `https://www.lawscoutai.com` were blocked by CORS.

**Fix:** Added `https://www.lawscoutai.com` to backend's `allow_origins` list.

**Files Changed:**
- `backend/main.py` - Added www subdomain to CORS origins

### Forbidden Header
**Issue:** Frontend was trying to set `Accept-Encoding` header (forbidden by browsers).

**Fix:** Removed `Accept-Encoding` from axios configuration (browsers handle automatically).

**Files Changed:**
- `frontend/src/app/page.tsx` - Removed forbidden header

**Status:** ✅ Both fixes deployed and working

---

## 📊 Performance Metrics

### Query Performance
- **Search Time:** ~1.5 seconds (vector + keyword search)
- **Generation Time:** ~8 seconds (Gemini API)
- **Total Response:** ~9-10 seconds
- **Cached Queries:** <100ms (cache hit)

### System Resources
- **Backend Memory:** ~1.2-1.8 GB (2 GB limit on Render)
- **Frontend Memory:** ~200-400 MB
- **Vector DB:** Qdrant Cloud (managed)

---

## 🔐 Security

### CORS
- ✅ Properly configured for production domains
- ✅ Credentials allowed (if needed)
- ✅ All HTTP methods allowed
- ✅ All headers allowed

### API Keys
- **Qdrant API Key:** Stored in Render environment variables
- **Gemini API Key:** Stored in Render environment variables
- **Never committed:** All keys in `.env` (gitignored)

### HTTPS
- ✅ All traffic encrypted (HTTPS)
- ✅ Cloudflare SSL/TLS termination
- ✅ Render SSL certificates

---

## 📝 Environment Variables

### Backend (Render)
```
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
GEMINI_API_KEY=your-gemini-key
PORT=8000
```

### Frontend (Render)
```
NEXT_PUBLIC_API_URL=https://lawscout-backend-latest.onrender.com
NODE_ENV=production
PORT=3000
```

---

## 🐛 Known Issues / Limitations

1. **Cold Starts:** Render services may spin down after inactivity (free tier)
   - **Impact:** First request after idle period may be slow
   - **Solution:** Upgrade to paid tier for always-on instances

2. **Rate Limiting:** Gemini API has rate limits
   - **Impact:** High traffic may hit rate limits
   - **Solution:** Implement request queuing or upgrade API tier

3. **Cache Invalidation:** Query cache doesn't expire automatically
   - **Impact:** Stale results for updated documents
   - **Solution:** Implement TTL-based cache expiration

---

## 🔄 Maintenance

### Regular Tasks
- Monitor Render service health
- Check Qdrant Cloud usage/quota
- Review Gemini API usage/costs
- Monitor Cloudflare analytics
- Review backend logs for errors

### Update Process
1. Make code changes
2. Test locally
3. Commit to git
4. Run `./scripts/deploy.sh`
5. Wait for Render to pull new images
6. Verify deployment via `/health` endpoint
7. Test on production domain

---

## 📚 Documentation

- **README.md** - Project overview
- **DEPLOYMENT.md** - Detailed deployment guide
- **DEPLOYMENT_QUICKSTART.md** - Quick deployment steps
- **docs/CLOUDFLARE_SETUP.md** - Cloudflare configuration
- **docs/CLOUDFLARE_API_FIX.md** - CORS troubleshooting

---

## 🎯 Current Status Summary

✅ **Frontend:** Operational on `www.lawscoutai.com`  
✅ **Backend:** Operational on Render  
✅ **CORS:** Properly configured  
✅ **CDN:** Cloudflare active and caching  
✅ **RAG System:** Fully functional  
✅ **Vector DB:** Connected to Qdrant Cloud  
✅ **AI Model:** Gemini 2.5 Flash working  
✅ **Deployment:** Automated via Docker images  

**Everything is working correctly!** 🎉

---

*This document is maintained to reflect the current state of the LawScout AI production system.*

