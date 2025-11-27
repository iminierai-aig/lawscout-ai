#!/bin/bash
set -e
echo "Deploying..."
if [ ! -f .env ]; then
    echo ".env not found"
    exit 1
fi
export $(cat .env | grep -v '^#' | xargs)
cd web_app
gcloud run deploy lawscout-ai --source . --region us-central1
echo "Deployed!"
