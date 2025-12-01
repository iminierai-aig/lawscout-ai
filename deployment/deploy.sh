#!/bin/bash
set -e

echo "🚀 Deploying LawScout AI to Cloud Run..."

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ .env not found"
    exit 1
fi

# Load environment variables (handle comments and empty lines properly)
set -a
source .env
set +a

# Validate required variables
if [ -z "$QDRANT_URL" ] || [ -z "$QDRANT_API_KEY" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Missing required environment variables (QDRANT_URL, QDRANT_API_KEY, GEMINI_API_KEY)"
    exit 1
fi

echo "📋 Configuration:"
echo "   Region: us-central1"
echo "   QDRANT_URL: ${QDRANT_URL:0:30}..."
echo "   Build timeout: 45 minutes (for large ML packages)"

# Deploy using cloudbuild.yaml with extended timeout
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions="_QDRANT_URL=$QDRANT_URL,_QDRANT_API_KEY=$QDRANT_API_KEY,_GEMINI_API_KEY=$GEMINI_API_KEY" \
    .

echo "✅ Deployed!"
echo "🌐 Check: https://console.cloud.google.com/run?project=$(gcloud config get-value project)"
