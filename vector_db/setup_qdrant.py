#!/usr/bin/env python3
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantSetup:
    def __init__(self):
        url = os.getenv('QDRANT_URL')
        api_key = os.getenv('QDRANT_API_KEY')
        if url and api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
        else:
            self.client = QdrantClient(":memory:")
    
    def create_collection(self, name, size=384):
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE)
        )

def main():
    setup = QdrantSetup()
    setup.create_collection("legal_cases", 384)

if __name__ == "__main__":
    main()
