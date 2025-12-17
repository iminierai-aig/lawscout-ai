FROM python:3.11-slim

WORKDIR /app

# create data directory for SQLite
RUN mkdir -p /app/data

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install NEWER CPU-only PyTorch (2.2.0 fixes the compatibility issue)
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Verify CPU version installed
RUN python -c "import torch; print(f'PyTorch {torch.__version__}'); assert not torch.cuda.is_available()"

# Install other dependencies - UPDATED FOR V2.0
RUN pip install --no-cache-dir \
    streamlit==1.31.1 \
    qdrant-client==1.11.3 \
    google-generativeai==0.8.3 \
    python-dotenv==1.0.1 \
    sentence-transformers==3.3.1 \
    rank-bm25==0.2.2 \
    transformers==4.46.3 \
    regex==2024.11.6 \
    pandas==2.2.3 \
    plotly==5.24.1

# Copy app code
COPY web_app/ ./web_app/
COPY rag_system/ ./rag_system/

EXPOSE 8501

CMD ["sh", "-c", "streamlit run web_app/app.py --server.port=${PORT:-8501} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]