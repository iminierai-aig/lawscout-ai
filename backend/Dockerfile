FROM python:3.10-slim

WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your EXISTING code (rag_system, vector_db, etc.)
COPY rag_system/ ./rag_system/
COPY vector_db/ ./vector_db/
COPY data_collection/ ./data_collection/

# Copy FastAPI code
COPY api/ ./api/
COPY main.py .

# Environment
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

# Run with gunicorn for production
CMD ["gunicorn", "main:app", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "300"]
