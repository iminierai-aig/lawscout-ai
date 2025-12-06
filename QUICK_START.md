# ⚡ Quick Start Guide - LawScout AI

## 🚀 Get Running in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file:
```bash
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_key
GEMINI_API_KEY=your_gemini_key
```

### 3. Run Application
```bash
streamlit run web_app/app.py
```

Visit: http://localhost:8501

---

## 🆕 New Features (Just Added!)

### ⚡ Streaming Responses
- Real-time answer generation
- See text appear character-by-character
- No more blank waiting screens

### 📜 Query History
- Sidebar shows last 10 queries
- One-click to rerun previous searches
- Automatic deduplication

### 📊 Analytics Dashboard
```bash
streamlit run monitoring/analytics_dashboard.py
```
- View query patterns
- Performance metrics
- Usage statistics
- Export data as CSV/JSON

### 📥 Export Results
- Download button in results
- Markdown format with citations
- Includes query + answer + sources

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=rag_system --cov=web_app --cov-report=html
```

### Install Dev Tools
```bash
pip install -r requirements-dev.txt
pre-commit install
```

---

## 📚 Documentation

- **Full Setup:** [SETUP.md](SETUP.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Improvements:** [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md)
- **Project Info:** [README.md](README.md)

---

## 🎯 Key Improvements Made

✅ Updated all dependencies to latest versions  
✅ Added real-time streaming responses  
✅ Implemented query history  
✅ Built comprehensive analytics system  
✅ Created professional test suite  
✅ Added export functionality  
✅ Enhanced UI with performance metrics  

---

## 🛠️ Quick Commands

```bash
# Development
streamlit run web_app/app.py              # Run main app
streamlit run monitoring/analytics_dashboard.py  # Analytics

# Testing
pytest tests/ -v                          # Run tests
black .                                   # Format code
flake8 rag_system/ web_app/              # Lint code

# Pre-commit
pre-commit install                        # Install hooks
pre-commit run --all-files               # Run all checks

# Docker
docker build -t lawscout-ai .            # Build image
docker run -p 8501:8501 lawscout-ai      # Run container
```

---

## 💡 Tips

- **First time?** Start with query history feature - try the quick search buttons
- **Slow responses?** Check analytics dashboard for performance insights
- **Want data?** Use export button to save research results
- **Contributing?** Read CONTRIBUTING.md for guidelines

---

## 🆘 Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"API key not configured"**
```bash
# Check .env file exists with correct keys
cat .env
```

**"Tests failing"**
```bash
# Ensure you're in virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

---

## 📧 Need Help?

- Check [SETUP.md](SETUP.md) for detailed instructions
- Review [IMPROVEMENTS_SUMMARY.md](IMPROVEMENTS_SUMMARY.md) for what's new
- Open an issue on GitHub for bugs

---

**Ready to go!** 🚀 Run `streamlit run web_app/app.py` to start.

