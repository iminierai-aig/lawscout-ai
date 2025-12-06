# 🚀 LawScout AI - Setup Guide

Complete guide for setting up and running LawScout AI locally and in production.

## 📋 Prerequisites

- **Python 3.11+** installed
- **Git** for version control
- **API Keys**:
  - [Qdrant Cloud](https://cloud.qdrant.io/) account (free tier available)
  - [Google Gemini API](https://aistudio.google.com/app/apikey) key
- **Optional**: Docker for containerized deployment

---

## 🏁 Quick Start (5 minutes)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/lawscout-ai.git
cd lawscout-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Or development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# Qdrant Vector Database
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
```

**Getting API Keys:**
- **Qdrant**: Sign up at [cloud.qdrant.io](https://cloud.qdrant.io/), create a cluster, copy URL and API key
- **Gemini**: Visit [aistudio.google.com](https://aistudio.google.com/app/apikey), click "Get API Key"

### 5. Run Application
```bash
streamlit run web_app/app.py
```

Visit `http://localhost:8501` in your browser.

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=rag_system --cov=web_app --cov-report=html

# View coverage report
open htmlcov/index.html  # On Mac
# Or navigate to htmlcov/index.html in your browser
```

### Run Specific Tests
```bash
# Unit tests only
pytest tests/test_rag_engine.py -v

# Integration tests (requires API keys)
pytest tests/test_integration.py -v
```

---

## 📊 Analytics Dashboard

View usage analytics and performance metrics:

```bash
streamlit run monitoring/analytics_dashboard.py
```

Analytics are automatically tracked during queries and saved to `analytics.json`.

---

## 🐳 Docker Deployment

### Build Image
```bash
docker build -t lawscout-ai .
```

### Run Container
```bash
docker run -p 8501:8501 \
  -e QDRANT_URL="your_url" \
  -e QDRANT_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  lawscout-ai
```

---

## ☁️ Cloud Deployment

### Google Cloud Run

1. **Install Google Cloud SDK**
   ```bash
   # Follow instructions at: https://cloud.google.com/sdk/docs/install
   gcloud init
   ```

2. **Set Environment Variables**
   ```bash
   # Edit deployment/deploy.sh with your values
   export QDRANT_URL="your_url"
   export QDRANT_API_KEY="your_key"
   export GEMINI_API_KEY="your_key"
   ```

3. **Deploy**
   ```bash
   chmod +x deployment/deploy.sh
   ./deployment/deploy.sh
   ```

### Alternative: Cloud Build
```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_QDRANT_URL="$QDRANT_URL",_QDRANT_API_KEY="$QDRANT_API_KEY",_GEMINI_API_KEY="$GEMINI_API_KEY"
```

---

## 🔧 Development Setup

### Install Development Tools
```bash
pip install -r requirements-dev.txt
```

### Set Up Pre-commit Hooks
```bash
pre-commit install
```

### Code Formatting
```bash
# Format code with Black
black .

# Lint with flake8
flake8 rag_system/ web_app/

# Type checking with mypy
mypy rag_system/ web_app/
```

### Interactive Development
```bash
# Start Jupyter notebook
jupyter notebook

# Or use IPython
ipython
```

---

## 📁 Project Structure

```
lawscout-ai/
├── rag_system/              # RAG engine & query handling
│   ├── rag_engine.py        # Core RAG implementation
│   └── query_handler.py     # Query processing
├── web_app/                 # Streamlit frontend
│   ├── app.py               # Main application
│   └── app_optimized.py     # Optimized version
├── tests/                   # Test suite
│   ├── test_rag_engine.py   # Unit tests
│   └── test_integration.py  # Integration tests
├── monitoring/              # Analytics & monitoring
│   ├── analytics_dashboard.py  # Analytics dashboard
│   ├── cost_tracker.py      # Cost tracking
│   └── dashboard.py         # System dashboard
├── data_collection/         # Data collection scripts
├── preprocessing/           # Text cleaning & chunking
├── embeddings/              # Embedding generation
├── vector_db/               # Qdrant setup & population
├── deployment/              # Deployment scripts
├── Dockerfile               # Container configuration
├── cloudbuild.yaml          # Cloud Build configuration
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md                # Project documentation
```

---

## 🎯 Features Overview

### ✅ Implemented Features

- ✅ **Streaming Responses** - Real-time LLM answer generation
- ✅ **Query History** - Track and revisit recent searches
- ✅ **Analytics Tracking** - Performance and usage metrics
- ✅ **Export Results** - Download research results as Markdown
- ✅ **Multi-collection Search** - Search contracts, cases, or both
- ✅ **Source Citations** - Transparent source attribution
- ✅ **Advanced Filters** - Customize search parameters
- ✅ **Dark Theme** - Modern, eye-friendly UI

### 🎨 UI Enhancements

- **Quick Search Buttons** - One-click common queries
- **Example Queries** - Categorized query templates
- **Collapsible Sections** - Organized sidebar
- **Performance Metrics** - Real-time latency tracking
- **Session Statistics** - Live usage stats

---

## 🛠️ Troubleshooting

### Issue: "Module not found"
```bash
# Ensure you're in the virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "API key not configured"
```bash
# Check .env file exists and has correct keys
cat .env

# Verify environment variables are loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### Issue: Slow response times
- Check your internet connection
- Verify Qdrant cluster is in a nearby region
- Consider upgrading to a larger Qdrant instance
- Monitor analytics dashboard for bottlenecks

### Issue: Docker build fails
```bash
# Clear Docker cache and rebuild
docker system prune -a
docker build --no-cache -t lawscout-ai .
```

---

## 📚 Additional Resources

- **Documentation**: [README.md](README.md)
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Gemini API**: https://ai.google.dev/docs
- **Streamlit Docs**: https://docs.streamlit.io/

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Code style and standards
- Pull request process
- Testing requirements
- Documentation standards

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

