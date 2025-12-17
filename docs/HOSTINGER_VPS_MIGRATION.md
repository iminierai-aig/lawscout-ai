# Hostinger VPS Migration Summary

**Migration Date:** December 2024  
**From:** Render.com  
**To:** Hostinger VPS (KVM4)

---

## 🏗️ Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Hostinger VPS KVM4                       │
│                    72.62.80.12                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Traefik    │  │   Dokploy    │  │  Qdrant DB      │  │
│  │   (Proxy)    │  │  (Manager)   │  │  (Vector Store) │  │
│  │   :80/:443   │  │   :3000      │  │   :6333/:6334   │  │
│  └──────┬───────┘  └──────────────┘  └────────┬────────┘  │
│         │                                      │            │
│         ├──────────────┬───────────────────────┤            │
│         │              │                       │            │
│  ┌──────▼───────┐ ┌───▼────────┐              │            │
│  │   Frontend   │ │   Backend  │◄─────────────┘            │
│  │   Next.js    │ │   FastAPI  │                           │
│  │   :3000      │ │   :8000    │                           │
│  └──────────────┘ └────────────┘                           │
│         │              │                                    │
│         │              │                                    │
│  ┌──────▼──────────────▼─────┐                            │
│  │      SQLite Database       │                            │
│  │    /app/data/users.db      │                            │
│  │  (User Auth & Search Log)  │                            │
│  └────────────────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌐 DNS Configuration (Cloudflare - DNS Only)

| Domain | IP | Service |
|--------|-----|---------|
| `lawscoutai.com` | 72.62.80.12 | Frontend (Next.js) |
| `www.lawscoutai.com` | 72.62.80.12 | Frontend (Next.js) |
| `api.lawscoutai.com` | 72.62.80.12 | Backend (FastAPI) |
| `dokploy.lawscoutai.com` | 72.62.80.12 | Dokploy (Management) |

---

## 📝 Configuration Changes

### Frontend Updates

**Files Updated:**
- `frontend/src/lib/api.ts` - API URL default changed to `https://api.lawscoutai.com`
- `frontend/src/app/page.tsx` - API URL default updated
- `frontend/next.config.js` - Environment variable default updated

**Changes:**
```typescript
// Before
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://lawscout-backend-latest.onrender.com';

// After
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.lawscoutai.com';
```

### Backend Updates

**Files Updated:**
- `backend/main.py` - CORS origins updated

**CORS Configuration:**
```python
allow_origins=[
    "https://lawscoutai.com",          # Production frontend
    "https://www.lawscoutai.com",       # Production frontend (www)
    "https://api.lawscoutai.com",       # Backend API domain
    "https://beta.lawscoutai.com",      # Beta domain
    "http://localhost:3000",            # Local dev
    "http://localhost:8501",            # Local Streamlit dev
]
```

### Deployment Scripts

**Files Updated:**
- `scripts/deploy.sh` - Default backend URL updated
- `scripts/deploy-frontend-only.sh` - Default backend URL updated

**Changes:**
```bash
# Before
BACKEND_URL="${BACKEND_URL:-https://lawscout-backend-latest.onrender.com}"

# After
BACKEND_URL="${BACKEND_URL:-https://api.lawscoutai.com}"
```

---

## 🔧 Environment Variables

### Frontend (Next.js)
```bash
NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
```

### Backend (FastAPI)
```bash
QDRANT_URL=http://qdrant:6333  # Internal Docker network
# OR
QDRANT_URL=http://localhost:6333  # If Qdrant is on host

QDRANT_API_KEY=your-qdrant-api-key
GEMINI_API_KEY=your-gemini-api-key
JWT_SECRET_KEY=your-jwt-secret-key
PORT=8000
```

---

## 🚀 Deployment Process

### Using Dokploy

1. **Connect Repository:**
   - Add your GitHub repository to Dokploy
   - Configure build settings

2. **Frontend Deployment:**
   - Build command: `npm run build`
   - Start command: `npm start`
   - Port: `3000`
   - Environment: `NEXT_PUBLIC_API_URL=https://api.lawscoutai.com`

3. **Backend Deployment:**
   - Build command: `docker build -t lawscout-backend .`
   - Start command: `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000`
   - Port: `8000`
   - Environment variables: See above

### Using Docker Compose (Alternative)

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.lawscoutai.com
    networks:
      - lawscout-network

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - QDRANT_URL=http://qdrant:6333
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./backend/data:/app/data
    networks:
      - lawscout-network

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
    networks:
      - lawscout-network

networks:
  lawscout-network:
    driver: bridge

volumes:
  qdrant_storage:
```

---

## 🔄 Traefik Configuration

Traefik should be configured to route:

- `lawscoutai.com` → Frontend (port 3000)
- `www.lawscoutai.com` → Frontend (port 3000)
- `api.lawscoutai.com` → Backend (port 8000)
- `dokploy.lawscoutai.com` → Dokploy (port 3000)

Example Traefik labels for Docker:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend.rule=Host(`lawscoutai.com`) || Host(`www.lawscoutai.com`)"
  - "traefik.http.routers.frontend.entrypoints=websecure"
  - "traefik.http.routers.frontend.tls.certresolver=letsencrypt"
  - "traefik.http.services.frontend.loadbalancer.server.port=3000"
  
  - "traefik.http.routers.backend.rule=Host(`api.lawscoutai.com`)"
  - "traefik.http.routers.backend.entrypoints=websecure"
  - "traefik.http.routers.backend.tls.certresolver=letsencrypt"
  - "traefik.http.services.backend.loadbalancer.server.port=8000"
```

---

## ✅ Migration Checklist

- [x] Update frontend API URLs
- [x] Update backend CORS configuration
- [x] Update deployment scripts
- [x] Configure DNS (Cloudflare)
- [ ] Deploy frontend to VPS
- [ ] Deploy backend to VPS
- [ ] Configure Traefik routing
- [ ] Test frontend → backend communication
- [ ] Test authentication endpoints
- [ ] Test search functionality
- [ ] Verify SSL certificates (Let's Encrypt)
- [ ] Update monitoring/health checks
- [ ] Update documentation

---

## 🔍 Testing

### Test Frontend
```bash
curl https://lawscoutai.com
curl https://www.lawscoutai.com
```

### Test Backend
```bash
curl https://api.lawscoutai.com/health
curl https://api.lawscoutai.com/api/auth/health
```

### Test API Integration
```bash
# Register user
curl -X POST https://api.lawscoutai.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123!", "full_name": "Test User"}'

# Login
curl -X POST https://api.lawscoutai.com/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!"
```

---

## 📊 Benefits of VPS Migration

1. **Cost Savings:** VPS is typically cheaper than managed services
2. **Full Control:** Complete control over infrastructure
3. **Performance:** Direct access to resources, no cold starts
4. **Flexibility:** Easy to scale and customize
5. **Data Locality:** All services on same network (lower latency)

---

## 🔐 Security Notes

- ✅ Use Traefik for SSL/TLS termination
- ✅ Configure firewall (UFW/iptables) to only allow necessary ports
- ✅ Keep Docker images updated
- ✅ Use strong JWT_SECRET_KEY
- ✅ Secure Qdrant with API keys
- ✅ Regular backups of SQLite database
- ✅ Monitor logs for suspicious activity

---

## 📚 Additional Resources

- [Dokploy Documentation](https://dokploy.com/docs)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

---

**Last Updated:** December 2024  
**Status:** ✅ Configuration updated, ready for deployment

