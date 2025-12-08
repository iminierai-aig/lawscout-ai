# Local Testing Scripts

Scripts to help you test LawScout AI locally before deploying to Render.com.

## Available Scripts

### Setup Scripts

#### `local-setup.sh`
One-time setup script that:
- Creates `.env` template
- Creates `frontend/.env.local`
- Sets up virtual environment
- Installs all dependencies

**Usage:**
```bash
./scripts/local-setup.sh
```

### Start Scripts

#### `start-backend.sh`
Starts the FastAPI backend server.

**Usage:**
```bash
./scripts/start-backend.sh
```

**What it does:**
- Activates virtual environment
- Checks for dependencies
- Starts server on http://localhost:8000

#### `start-frontend.sh`
Starts the Next.js frontend server.

**Usage:**
```bash
./scripts/start-frontend.sh
```

**What it does:**
- Installs dependencies if needed
- Creates `.env.local` if missing
- Starts dev server on http://localhost:3000

### Test Scripts

#### `test-backend.sh`
Tests the backend API endpoints.

**Usage:**
```bash
./scripts/test-backend.sh
```

**What it tests:**
- Health endpoint
- API documentation
- Search endpoint

#### `test-integration.sh`
Tests the full integration (backend + frontend).

**Usage:**
```bash
./scripts/test-integration.sh
```

**What it tests:**
- Backend is running
- Frontend is running
- API connection works
- CORS configuration

## Quick Start

1. **First time setup:**
   ```bash
   ./scripts/local-setup.sh
   ```

2. **Edit `.env` with your API keys**

3. **Start backend (Terminal 1):**
   ```bash
   ./scripts/start-backend.sh
   ```

4. **Start frontend (Terminal 2):**
   ```bash
   ./scripts/start-frontend.sh
   ```

5. **Test integration:**
   ```bash
   ./scripts/test-integration.sh
   ```

6. **Open browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs

## Requirements

- Python 3.11+
- Node.js 20+
- API keys (Qdrant, Gemini)

## Troubleshooting

### Scripts not executable
```bash
chmod +x scripts/*.sh
```

### Scripts not found
Make sure you're in the project root directory.

### Backend won't start
- Check `.env` file exists
- Check virtual environment is activated
- Check dependencies are installed

### Frontend won't start
- Check `frontend/.env.local` exists
- Check `npm install` completed
- Check Node.js version (20+)

## See Also

- `LOCAL_TESTING.md` - Complete testing guide
- `QUICK_START_LOCAL.md` - Quick reference
- `RENDER_DEPLOYMENT.md` - Deployment guide

