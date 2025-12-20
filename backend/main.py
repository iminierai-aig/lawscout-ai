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
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from auth import router as auth_router, init_db

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
    """Initialize database and RAG engine on startup"""
    global rag_engine
    
    # Initialize database first (critical for auth)
    logger = logging.getLogger(__name__)
    logger.info("🗄️  Initializing database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
        print("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        print(f"❌ Failed to initialize database: {e}")
        raise
    
    # Initialize RAG engine
    logger.info("🚀 Initializing LawScout AI RAG Engine...")
    print("🚀 Initializing LawScout AI RAG Engine...")
    try:
        rag_engine = LegalRAGEngine()
        # Store in app state for easy access in routes
        app.state.rag_engine = rag_engine
        logger.info("✅ RAG Engine ready!")
        print("✅ RAG Engine ready!")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG engine: {e}", exc_info=True)
        print(f"❌ Failed to initialize RAG engine: {e}")
        raise
    
    # Log initial usage stats (non-blocking - don't fail startup if this fails)
    try:
        from rag_system.usage_tracker import get_usage_tracker
        tracker = get_usage_tracker()
        tracker.log_stats()
    except Exception as e:
        logger.warning(f"⚠️  Could not initialize usage tracker (non-critical): {e}")
        print(f"⚠️  Could not initialize usage tracker (non-critical): {e}")
    
    yield  # Server runs here
    
    logger.info("👋 Shutting down RAG engine...")
    print("👋 Shutting down RAG engine...")

# Create FastAPI app
app = FastAPI(
    title="LawScout AI API",
    version="2.1.1",
    lifespan=lifespan
)

# Session middleware for OAuth (must be before other middleware)
import os
SESSION_SECRET = os.getenv("SESSION_SECRET", os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION"))
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# Response compression - reduces network transfer time significantly
# This works great with Cloudflare CDN which also compresses responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS - Allow both old (Streamlit) and new (Next.js) frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lawscoutai.com",                    # ✅ Production frontend domain
        "https://www.lawscoutai.com",                # ✅ Production frontend domain with www
        "https://api.lawscoutai.com",                # ✅ Backend API domain (for API docs)
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

# INclude auth routes
app.include_router(auth_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info"
    )
