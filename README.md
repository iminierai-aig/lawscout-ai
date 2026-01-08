# ⚖️ LawScout AI

**AI-Powered Legal Research Assistant**

🌐 **Live at:** [www.lawscoutai.com](https://www.lawscoutai.com)

240,633 legal documents • Qdrant Cloud • Gemini-powered RAG  
Built solo in 2025 — no funding, no team.

---

## 🎯 What is LawScout AI?

LawScout AI is an affordable, AI-powered legal research tool designed for solo practitioners and small law firms. It uses RAG (Retrieval Augmented Generation) to search through legal documents and generate answers with citations.

### Features

- **240K+ Legal Documents** - Federal case law + commercial contracts
- **Hybrid Search** - Semantic understanding + keyword matching (BM25)
- **ML-Powered Reranking** - Cross-encoder for improved relevance
- **Citation Extraction** - Automatic legal citation detection with CourtListener links
- **AI-Generated Answers** - Powered by Gemini 2.5 Flash with source citations
- **Fast Response** - ~9-10 second total response time (search + generation)
- **Modern Web UI** - Next.js frontend with Harvey.ai-inspired design
- **Production Ready** - Deployed on Render.com with Cloudflare CDN

---

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- [Qdrant Cloud](https://cloud.qdrant.io/) account (free tier)
- [Gemini API key](https://aistudio.google.com/app/apikey)

### Local Development

#### Backend Setup

```bash
# Clone repository
git clone https://github.com/iminierai-aig/lawscout-ai.git
cd lawscout-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys:
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your-api-key
# GEMINI_API_KEY=your-gemini-key

# Run backend
cd backend
uvicorn main:app --reload --port 8000
```

#### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Configure environment
# Create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run frontend
npm run dev
```

The frontend will be available at `http://localhost:3000` and will connect to the backend at `http://localhost:8000`.

### Production Deployment

Deploy to Render.com using Docker:

```bash
./scripts/deploy.sh
```

This builds and pushes Docker images to GitHub Container Registry, which Render automatically pulls.

See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for detailed deployment instructions.

---

## 📁 Project Structure

```
lawscout-ai/
├── backend/                 # FastAPI backend service
│   ├── api/                 # API routes
│   ├── auth/                # Authentication
│   ├── rag_system/          # RAG engine & query handling
│   │   ├── rag_engine.py    # Core RAG with hybrid search
│   │   ├── hybrid_search.py # Hybrid search & reranking
│   │   ├── citation_utils.py# Citation extraction
│   │   └── query_handler.py # Query processing
│   ├── vector_db/           # Qdrant setup & population
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/                # Next.js frontend
│   ├── src/
│   │   └── app/             # Next.js app directory
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile           # Frontend container
├── tests/                   # Test suite
├── deployment/              # Deployment scripts
├── data_collection/         # Data collection scripts
├── preprocessing/           # Text cleaning & chunking
├── embeddings/              # Embedding generation
├── scripts/                 # Utility scripts
└── docs/                    # Documentation
```

---

## 📊 Data Sources

- **CourtListener** - Federal case law from the [Free Law Project](https://free.law/)
- **CUAD Dataset** - Commercial contracts from [Atticus Project](https://www.atticusprojectai.org/cuad)

**Statistics:**
- **Total Documents:** 240,633
- **Total Chunks:** 171,813
- **Vector Dimensions:** 384 (all-MiniLM-L6-v2)

All data is public domain / freely available.

---

## 🎯 Core Principles

LawScout AI is built on four core principles that guide all development:

1. **Search Relevance** - Prioritize the most relevant results, especially for state-specific queries
2. **Organization** - Clear, well-structured presentation with complete metadata
3. **Truthfulness** - Honest, accurate answers with proper source attribution
4. **Citation Usefulness** - Accurate, linkable citations in proper legal format

See [docs/CORE_PRINCIPLES.md](docs/CORE_PRINCIPLES.md) for detailed development guidelines.

---

## 🌐 Production Deployment

**Status:** ✅ Fully Operational

- **Primary Domain:** [www.lawscoutai.com](https://www.lawscoutai.com)
- **Frontend:** Next.js on Render.com (Docker)
- **Backend:** FastAPI on Render.com (Docker)
- **CDN:** Cloudflare (edge caching, DDoS protection)
- **Vector DB:** Qdrant Cloud
- **AI Model:** Google Gemini 2.5 Flash

See [LAWSCOUTAI_CURRENT_STATE.md](LAWSCOUTAI_CURRENT_STATE.md) for detailed system architecture and deployment information.

---

## ⚠️ Disclaimer

LawScout AI is a **research tool only** and does not provide legal advice. All results should be verified with authoritative sources. Always consult qualified legal professionals for legal matters.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [Free Law Project](https://free.law/) - CourtListener data
- [Atticus Project](https://www.atticusprojectai.org/) - CUAD dataset
- [Qdrant](https://qdrant.tech/) - Vector database
- [Google](https://ai.google.dev/) - Gemini API
