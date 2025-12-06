# Contributing to LawScout AI

Thank you for considering contributing to LawScout AI! This document provides guidelines and instructions for contributing.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment
- Follow professional communication standards

## 🚀 How to Contribute

### Reporting Bugs 🐛

1. **Check existing issues** - Search for similar problems first
2. **Create detailed report** - Include:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Error messages and logs
   - Screenshots if applicable

### Suggesting Features 💡

1. **Check roadmap** - Review README.md for planned features
2. **Open discussion** - Create an issue with:
   - Clear use case description
   - Expected benefits
   - Potential implementation approach
   - Examples from similar tools (if any)

### Contributing Code 👨‍💻

#### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/lawscout-ai.git
cd lawscout-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### Creating a Pull Request

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Check code formatting
   black .
   
   # Run linter
   flake8 rag_system/ web_app/
   
   # Type checking
   mypy rag_system/ web_app/
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add descriptive commit message"
   ```
   
   **Commit Message Format:**
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements
   - `chore:` - Maintenance tasks

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then open a Pull Request on GitHub with:
   - Clear title and description
   - Link to related issues
   - Screenshots/GIFs for UI changes
   - Testing instructions

## 📝 Code Standards

### Python Style Guide

- **PEP 8** - Follow Python style guidelines
- **Black** - Use Black for code formatting (line length: 100)
- **Type hints** - Add type annotations for functions
- **Docstrings** - Document all public functions/classes

Example:
```python
def search_documents(
    query: str,
    collection_type: str = 'both',
    limit: int = 5
) -> List[Dict]:
    """
    Search vector database for relevant documents.
    
    Args:
        query: Search query string
        collection_type: Type of collection to search ('contracts', 'cases', 'both')
        limit: Maximum number of results to return
    
    Returns:
        List of document dictionaries with scores and metadata
    
    Raises:
        ValueError: If collection_type is invalid
    """
    # Implementation here
    pass
```

### Testing Standards

- **Unit tests** - Test individual functions/classes
- **Integration tests** - Test component interactions
- **Mock external APIs** - Use pytest-mock for API calls
- **Coverage goal** - Aim for 80%+ code coverage
- **Test naming** - Use descriptive test names

Example:
```python
def test_search_returns_correct_number_of_results():
    """Test that search returns exactly the requested number of results"""
    engine = LegalRAGEngine()
    results = engine.search("test query", limit=5)
    assert len(results) == 5
```

### Documentation Standards

- **README.md** - Keep updated with new features
- **Docstrings** - Document all public APIs
- **Comments** - Explain complex logic
- **Type hints** - Add for better IDE support
- **Examples** - Provide usage examples

## 🏗️ Architecture Guidelines

### Adding New Features

1. **RAG Engine** (`rag_system/rag_engine.py`)
   - Core search and generation logic
   - Keep methods focused and testable
   - Add analytics tracking for new operations

2. **Web App** (`web_app/app.py`)
   - UI components and user interactions
   - Use Streamlit best practices
   - Maintain responsive design
   - Add proper error handling

3. **Query Handler** (`rag_system/query_handler.py`)
   - Query preprocessing and routing
   - Add new query patterns carefully
   - Test with diverse inputs

### File Organization

```
new_feature/
├── implementation.py    # Core logic
├── __init__.py         # Module exports
├── tests/
│   ├── test_implementation.py
│   └── test_integration.py
└── README.md           # Feature documentation
```

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests** - Fast, isolated, no external dependencies
2. **Integration Tests** - Test component interactions
3. **E2E Tests** - Test complete user flows
4. **Performance Tests** - Benchmark critical paths

### Writing Good Tests

```python
# Good: Descriptive, isolated, single assertion focus
def test_search_handles_empty_query_gracefully():
    """Test that search returns empty results for empty query"""
    engine = LegalRAGEngine()
    results = engine.search("")
    assert results == []

# Bad: Vague name, multiple responsibilities
def test_search():
    # Tests too many things at once
    pass
```

### Test Coverage

```bash
# Run with coverage
pytest tests/ --cov=rag_system --cov=web_app --cov-report=html

# View report
open htmlcov/index.html
```

## 📊 Performance Considerations

- **Caching** - Cache expensive operations (embeddings, LLM responses)
- **Async operations** - Use asyncio for I/O bound tasks
- **Batch processing** - Process multiple items together when possible
- **Monitoring** - Add timing logs for new features
- **Memory** - Be mindful of memory usage with large datasets

## 🔒 Security Guidelines

- **Input validation** - Sanitize all user inputs
- **API keys** - Never commit secrets to git
- **Rate limiting** - Implement for public endpoints
- **Error messages** - Don't expose sensitive information
- **Dependencies** - Keep dependencies updated

## 📋 Pull Request Checklist

Before submitting your PR, ensure:

- [ ] Code follows style guidelines (Black, flake8)
- [ ] All tests pass (`pytest tests/ -v`)
- [ ] New tests added for new features
- [ ] Documentation updated (README, docstrings)
- [ ] Type hints added
- [ ] No linting errors
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete
- [ ] Related issues are linked

## 🎯 Priority Areas

We especially welcome contributions in these areas:

1. **Testing** - Expand test coverage
2. **Performance** - Optimize slow operations
3. **Documentation** - Improve guides and examples
4. **Features** - Implement roadmap items
5. **Bug fixes** - Address open issues
6. **Data quality** - Improve chunking, embeddings
7. **UI/UX** - Enhance user interface

## 📞 Getting Help

- **Questions?** - Open a discussion on GitHub
- **Stuck?** - Comment on your PR for guidance
- **Ideas?** - Share in issues or discussions

## 🎉 Recognition

Contributors will be:
- Listed in README.md
- Credited in release notes
- Recognized in project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to LawScout AI! 🙏

