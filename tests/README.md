# LawScout AI Test Suite

## Running Tests

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run specific test file
```bash
python -m pytest tests/test_rag_engine.py -v
```

### Run with coverage
```bash
python -m pytest tests/ --cov=rag_system --cov=web_app --cov-report=html
```

## Test Structure

- `test_rag_engine.py` - Unit tests for RAG engine
- `test_integration.py` - Integration tests (requires API keys)
- `test_performance.py` - Performance benchmarks (future)

## Environment Setup

For integration tests, set environment variables:
```bash
export QDRANT_URL="your_qdrant_url"
export QDRANT_API_KEY="your_api_key"
export GEMINI_API_KEY="your_gemini_key"
```

Or create a `.env.test` file (not committed to git).

## CI/CD

Tests run automatically on:
- Pull requests
- Commits to main branch
- Pre-deployment checks

## Adding Tests

1. Create test file: `test_<feature>.py`
2. Follow naming convention: `test_<functionality>`
3. Use fixtures for common setup
4. Mock external API calls
5. Document test purpose

