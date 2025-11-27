#!/usr/bin/env python3
import json
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import torch

class LocalEmbedder:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = SentenceTransformer(model_name, device=device)
        print(f"Using {device}")
    
    def process_dataset(self, input_file, output_file):
        print("Generating embeddings...")

def main():
    embedder = LocalEmbedder()

if __name__ == "__main__":
    main()
