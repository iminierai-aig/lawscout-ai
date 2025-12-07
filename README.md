# ⚖️ LawScout AI

**AI-Powered Legal Research Assistant**

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
- **Fast Response** - 3-4 second query times
- **Cloud Native** - Deploys to Google Cloud Run or Render

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│   RAG Engine    │─────▶│  Gemini API  │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│  Qdrant Cloud   │
│  (171K vectors) │
└─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Qdrant Cloud](https://cloud.qdrant.io/) account (free tier)
- [Gemini API key](https://aistudio.google.com/app/apikey)
- [Google Cloud](https://console.cloud.google.com/) account (for deployment)

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/lawscout-ai.git
cd lawscout-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Run locally
streamlit run web_app/app.py
```

### Deploy to Cloud Run

```bash
./deployment/deploy.sh
```

---

## 📁 Project Structure

```
lawscout-ai/
├── rag_system/              # RAG engine & query handling
│   ├── rag_engine.py        # Core RAG with hybrid search
│   ├── hybrid_search.py     # Hybrid search & reranking
│   ├── citation_utils.py    # Citation extraction
│   └── query_handler.py     # Query processing
├── web_app/                 # Streamlit frontend
│   └── app.py               # Main application
├── tests/                   # Test suite
├── deployment/              # Deployment scripts
├── data_collection/         # Data collection scripts
├── preprocessing/           # Text cleaning & chunking
├── embeddings/              # Embedding generation
├── vector_db/               # Qdrant setup & population
├── Dockerfile               # Container configuration
├── cloudbuild.yaml          # Cloud Build configuration
└── requirements.txt         # Python dependencies
```

---

## 📊 Data Sources

- **CourtListener** - Federal case law from the [Free Law Project](https://free.law/)
- **CUAD Dataset** - Commercial contracts from [Atticus Project](https://www.atticusprojectai.org/cuad)

All data is public domain / freely available.

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
