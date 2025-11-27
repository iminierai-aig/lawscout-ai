"""
Embedding Generation for Google Colab
Generates embeddings using sentence-transformers on FREE GPU
"""
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm
import numpy as np

print("🔧 Setup")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Configuration
MODEL_NAME = "all-MiniLM-L6-v2"  # Fast, good quality, 384 dimensions
BATCH_SIZE = 32
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"\n⚙️  Configuration:")
print(f"   Model: {MODEL_NAME}")
print(f"   Device: {DEVICE}")
print(f"   Batch size: {BATCH_SIZE}")

# Load model
print(f"\n📥 Loading model...")
model = SentenceTransformer(MODEL_NAME, device=DEVICE)
print(f"✅ Model loaded on {DEVICE}")

def generate_embeddings(chunks_file: str, output_file: str):
    """Generate embeddings for chunks"""
    
    # Load chunks
    print(f"\n📂 Loading chunks from {chunks_file}...")
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Extract texts
    texts = [chunk['text'] for chunk in chunks]
    
    # Generate embeddings in batches
    print(f"\n🔄 Generating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    print(f"   Shape: {embeddings.shape}")
    print(f"   Dtype: {embeddings.dtype}")
    
    # Add embeddings to chunks
    print(f"\n💾 Adding embeddings to chunks...")
    for i, chunk in enumerate(tqdm(chunks, desc="Processing")):
        chunk['embedding'] = embeddings[i].tolist()
    
    # Save with embeddings
    print(f"\n💾 Saving to {output_file}...")
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(chunks, f)
    
    file_size = Path(output_file).stat().st_size / (1024 * 1024)
    print(f"✅ Saved {len(chunks)} chunks with embeddings ({file_size:.2f} MB)")
    
    return chunks

def main():
    """Main embedding generation pipeline"""
    
    print("\n" + "=" * 60)
    print("🎯 Embedding Generation Pipeline")
    print("=" * 60)
    
    # Check for chunks directory
    chunks_dir = Path("data/chunks")
    if not chunks_dir.exists():
        print(f"❌ Chunks directory not found: {chunks_dir}")
        print("💡 Mount Google Drive and navigate to your project folder")
        return
    
    # Generate CUAD embeddings
    cuad_input = chunks_dir / "cuad_chunks.json"
    cuad_output = Path("data/embeddings") / "cuad_embeddings.json"
    
    if cuad_input.exists():
        print(f"\n�� Processing CUAD...")
        generate_embeddings(str(cuad_input), str(cuad_output))
    
    # Generate CourtListener embeddings
    cl_input = chunks_dir / "courtlistener_chunks.json"
    cl_output = Path("data/embeddings") / "courtlistener_embeddings.json"
    
    if cl_input.exists():
        print(f"\n⚖️  Processing CourtListener...")
        generate_embeddings(str(cl_input), str(cl_output))
    
    print("\n" + "=" * 60)
    print("✅ Embedding Generation Complete!")
    print("=" * 60)
    print("📁 Output files:")
    print(f"   • {cuad_output}")
    print(f"   • {cl_output}")
    print("\n🎯 Next: Download embeddings and upload to Qdrant")
    print("=" * 60)

if __name__ == "__main__":
    main()
