# GitHub Copilot Instructions for LawScout AI

## Project Overview

**LawScout AI** is an AI-powered legal research assistant using RAG (Retrieval Augmented Generation) to search through legal documents and generate answers with citations.

**Key Features:**
- Hybrid search (semantic + BM25 keyword matching)
- ML-powered reranking with cross-encoder
- Citation extraction with CourtListener links
- Gemini 2.5 Flash integration
- Streamlit web interface

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: Streamlit
- **Vector Database**: Qdrant Cloud
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Deployment**: Docker, Google Cloud Run, Render
- **Issue Tracking**: bd (beads)

## Coding Guidelines

### Testing
- Always write tests for new features
- Run `pytest tests/ -v` before committing
- Test coverage goal: 85%+
- Use mocks for external API calls

### Code Style
- Follow PEP 8 guidelines
- Use type hints for functions
- Add docstrings to all public functions
- Run `black .` and `flake8` before committing

### Git Workflow
- Always commit `.beads/issues.jsonl` with code changes if using bd
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, etc.
- Keep commits atomic and focused

## Issue Tracking with bd

**CRITICAL**: This project uses **bd (beads)** for ALL task tracking. Do NOT create markdown TODO lists.

### Essential Commands

```bash
# Find work
bd ready --json                    # Unblocked issues
bd stale --days 30 --json          # Forgotten issues

# Create and manage
bd create "Title" -t bug|feature|task -p 0-4 --json
bd create "Subtask" --parent <epic-id> --json  # Hierarchical subtask
bd update <id> --status in_progress --json
bd close <id> --reason "Done" --json

# Search
bd list --status open --priority 1 --json
bd show <id> --json

# Sync (CRITICAL at end of session!)
bd sync  # Force immediate export/commit/push
```

### Workflow

1. **Check ready work**: `bd ready --json`
2. **Claim task**: `bd update <id> --status in_progress`
3. **Work on it**: Implement, test, document
4. **Discover new work?** `bd create "Found bug" -p 1 --deps discovered-from:<parent-id> --json`
5. **Complete**: `bd close <id> --reason "Done" --json`
6. **Sync**: `bd sync` (flushes changes to git immediately)

### Priorities

- `0` - Critical (security, data loss, broken builds)
- `1` - High (major features, important bugs)
- `2` - Medium (default, nice-to-have)
- `3` - Low (polish, optimization)
- `4` - Backlog (future ideas)

## Project Structure

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

## Key Documentation

- **README.md** - Main project documentation
- **SETUP.md** - Setup and installation guide
- **CONTRIBUTING.md** - Contribution guidelines
- **AGENTS.md** - Comprehensive AI agent guide with bd workflow
- **Deployment_checklist.md** - Deployment reference

## Important Rules

- ✅ Use bd for ALL task tracking
- ✅ Always use `--json` flag for programmatic use
- ✅ Run `bd sync` at end of sessions
- ✅ Write tests for new features
- ✅ Run `bd <cmd> --help` to discover available flags
- ✅ Store AI planning docs in `history/` directory
- ❌ Do NOT create markdown TODO lists
- ❌ Do NOT use external issue trackers
- ❌ Do NOT duplicate tracking systems

---

**For detailed workflows and advanced features, see [AGENTS.md](../AGENTS.md)**

