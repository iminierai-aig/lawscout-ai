"""
Generate Embeddings using Google Vertex AI
Cost: ~$1.25 for 100K documents
"""

import json
import os
from pathlib import Path
from tqdm import tqdm
from google.cloud import aiplatform
from vertexai.language_models import TextEmbeddingModel
import time

class VertexAIEmbedder:
    """Generate embeddings using Vertex AI"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        """
        Initialize Vertex AI embedder
        
        Args:
            project_id: GCP project ID
            location: GCP region
        """
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        
        # Load embedding model
        self.model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        
        print(f"✅ Initialized Vertex AI in {project_id}/{location}")
    
    def generate_embeddings_batch(self, texts: list, batch_size: int = 250) -> list:
        """
        Generate embeddings in batches
        
        Args:
            texts: List of text strings
            batch_size: Number of texts per batch (max 250 for Vertex AI)
        
        Returns:
            List of embedding vectors
        """
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i+batch_size]
            
            try:
                # Generate embeddings for batch
                embeddings = self.model.get_embeddings(batch)
                
                # Extract embedding values
                batch_embeddings = [emb.values for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting (5 requests per second)
                time.sleep(0.2)
                
            except Exception as e:
                print(f"\n⚠️ Error on batch {i//batch_size}: {e}")
                # Retry with smaller batch
                if len(batch) > 1:
                    for text in batch:
                        try:
                            emb = self.model.get_embeddings([text])
                            all_embeddings.append(emb[0].values)
                            time.sleep(0.3)
                        except Exception as retry_error:
                            print(f"Failed to embed text: {retry_error}")
                            # Add zero vector as placeholder
                            all_embeddings.append([0.0] * 768)
        
        return all_embeddings
    
    def process_dataset(self, input_file: Path, output_file: Path, 
                       batch_size: int = 250):
        """
        Generate embeddings for entire dataset
        
        Args:
            input_file: Path to chunked JSON data
            output_file: Path to save embeddings
            batch_size: Batch size for API calls
        """
        print(f"📖 Loading data from {input_file}...")
        
        with open(input_file, 'r') as f:
            documents = json.load(f)
        
        print(f"🧠 Generating embeddings for {len(documents)} documents...")
        print(f"💰 Estimated cost: ${len(documents) * 1000 * 0.025 / 1_000_000:.2f}")
        
        # Extract texts
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts, batch_size)
        
        # Combine documents with embeddings
        embedded_documents = []
        for doc, embedding in zip(documents, embeddings):
            doc['embedding'] = embedding
            embedded_documents.append(doc)
        
        # Save to file
        print(f"💾 Saving embeddings to {output_file}...")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(embedded_documents, f)
        
        print(f"\n✅ Generated {len(embedded_documents)} embeddings")
        print(f"📊 Embedding dimension: {len(embeddings[0])}")
        
        # Calculate actual cost
        total_tokens = sum(len(text.split()) * 1.3 for text in texts)  # Approx tokens
        actual_cost = total_tokens * 0.025 / 1_000_000
        print(f"💰 Actual cost: ~${actual_cost:.2f}")


def main():
    """Main execution"""
    # Get GCP project ID from environment
    project_id = os.getenv('GCP_PROJECT_ID')
    if not project_id:
        print("❌ Error: Set GCP_PROJECT_ID environment variable")
        return
    
    embedder = VertexAIEmbedder(project_id=project_id)
    
    # Process CourtListener data
    cl_input = Path("data/processed/courtlistener_chunked.json")
    cl_output = Path("data/embeddings/courtlistener_embedded.json")
    
    if cl_input.exists():
        print("🚀 Embedding CourtListener data...")
        embedder.process_dataset(cl_input, cl_output)
    
    # Process CUAD data
    cuad_input = Path("data/processed/cuad_chunked.json")
    cuad_output = Path("data/embeddings/cuad_embedded.json")
    
    if cuad_input.exists():
        print("\n🚀 Embedding CUAD data...")
        embedder.process_dataset(cuad_input, cuad_output)
    
    print("\n✅ All embeddings generated!")


if __name__ == "__main__":
    main()