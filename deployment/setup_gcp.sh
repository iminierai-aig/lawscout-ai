#!/bin/bash
set -e
echo "Setting up GCP..."
PROJECT_ID="${GCP_PROJECT_ID:-}"
if [ -z "$PROJECT_ID" ]; then
    echo "Set GCP_PROJECT_ID"
    exit 1
fi
gcloud config set project $PROJECT_ID
gcloud services enable compute.googleapis.com
gcloud services enable run.googleapis.com
echo "Done!"
