"""
LawScout AI - FastAPI Backend
Wraps existing RAG engine without modifying it
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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
    version="2.1.0",
    lifespan=lifespan
)

# CORS - Allow both old (Streamlit) and new (Next.js) frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://lawscoutai.com",           # Current Streamlit
        "https://beta.lawscoutai.com",      # New Next.js
        "http://localhost:3000",            # Local Next.js dev
        "http://localhost:8501",            # Local Streamlit dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {
        "status": "healthy",
        "rag_engine": "initialized" if rag_engine else "not_initialized"
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
