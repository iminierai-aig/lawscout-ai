"""
LawScout AI - FastAPI Backend
Wraps existing RAG engine without modifying it
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Setup logging to file
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "backend.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Also log to console
    ]
)

# Load environment variables
load_dotenv()

# Import your existing RAG engine (NO CHANGES TO YOUR CODE!)
from rag_system.rag_engine import LegalRAGEngine

# Global RAG engine instance
rag_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG engine on startup"""
    global rag_engine
    print("🚀 Initializing LawScout AI RAG Engine...")
    
    try:
        rag_engine = LegalRAGEngine()
        # Store in app state for easy access in routes
        app.state.rag_engine = rag_engine
        print("✅ RAG Engine ready!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG engine: {e}")
        raise
    
    yield  # Server runs here
    
    print("👋 Shutting down RAG engine...")

# Create FastAPI app
app = FastAPI(
    title="LawScout AI API",
    version="2.1.1",
    lifespan=lifespan
)

# Response compression - reduces network transfer time significantly
# This works great with Cloudflare CDN which also compresses responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - Allow both old (Streamlit) and new (Next.js) frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lawscoutai.com",                    # ✅ Cloudflare-proxied domain (REQUIRED - users access this)
        "https://www.lawscoutai.com",                # ✅ Cloudflare-proxied domain with www (REQUIRED)
        "https://lawscout-frontend-latest.onrender.com",  # Render frontend origin (direct access)
        "https://lawscout-backend-latest.onrender.com",   # Backend origin (for API docs)
        "https://beta.lawscoutai.com",               # Beta domain (if used)
        "http://localhost:3000",                     # Local Next.js dev
        "http://localhost:8501",                     # Local Streamlit dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check for monitoring"""
    import psutil
    import os
    
    memory_mb = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    
    return {
        "status": "healthy",
        "rag_engine": "initialized" if rag_engine else "not_initialized",
        "memory_mb": round(memory_mb, 2),
        "memory_warning": memory_mb > 1800  # Warn if > 90% of 2GB
    }

# Import routes
from api.routes import router
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
