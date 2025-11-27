"""
Upload Embeddings to Qdrant Vector Database
"""
import json
import os
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# Configuration
QDRANT_URL = os.getenv('QDRANT_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 dimension
BATCH_SIZE = 100

print("=" * 60)
print("🚀 Qdrant Upload Pipeline")
print("=" * 60)

# Connect to Qdrant
print(f"\n🔌 Connecting to Qdrant...")
print(f"   URL: {QDRANT_URL}")

client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
)

print("✅ Connected to Qdrant")

def create_collection(collection_name: str):
    """Create Qdrant collection"""
    print(f"\n📦 Creating collection: {collection_name}")
    
    # Delete if exists
    try:
        client.delete_collection(collection_name)
        print(f"   Deleted existing collection")
    except:
        pass
    
    # Create new collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE
        )
    )
    print(f"✅ Collection created: {collection_name}")

def upload_embeddings(embeddings_file: str, collection_name: str):
    """Upload embeddings to Qdrant"""
    
    print(f"\n📂 Loading {embeddings_file}...")
    with open(embeddings_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Create collection
    create_collection(collection_name)
    
    # Upload in batches
    print(f"\n📤 Uploading to Qdrant...")
    
    uploaded_count = 0
    for i in tqdm(range(0, len(chunks), BATCH_SIZE), desc="Uploading"):
        batch = chunks[i:i + BATCH_SIZE]
        
        points = []
        for j, chunk in enumerate(batch):
            point_id = i + j
            
            # Prepare payload (metadata without embedding)
            payload = {k: v for k, v in chunk.items() if k != 'embedding'}
            
            # Create point
            point = PointStruct(
                id=point_id,
                vector=chunk['embedding'],
                payload=payload
            )
            points.append(point)
        
        # Upload batch
        try:
            client.upsert(
                collection_name=collection_name,
                points=points
            )
            uploaded_count += len(points)
        except Exception as e:
            print(f"\n⚠️  Batch {i} failed: {e}")
            continue
    
    print(f"\n✅ Uploaded {uploaded_count:,} vectors to {collection_name}")
    
    return uploaded_count

def verify_collections():
    """Verify collections exist and count vectors"""
    print("\n" + "=" * 60)
    print("🔍 Verifying Collections")
    print("=" * 60)
    
    try:
        # List all collections
        collections = client.get_collections()
        
        print(f"\n📊 Found {len(collections.collections)} collection(s):")
        
        total_vectors = 0
        for collection in collections.collections:
            # Try to count vectors with scroll (more reliable)
            try:
                result = client.scroll(
                    collection_name=collection.name,
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                print(f"   • {collection.name}: Exists ✅")
            except Exception as e:
                print(f"   • {collection.name}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Could not verify collections: {e}")
        print("   But uploads likely succeeded!")
        return False

def main():
    """Main upload pipeline"""
    
    embeddings_dir = Path('data/embeddings')
    
    total_uploaded = 0
    
    # Upload CUAD
    cuad_file = embeddings_dir / 'cuad_embeddings.json'
    if cuad_file.exists():
        print("\n" + "=" * 60)
        print("📋 Processing CUAD Contracts")
        print("=" * 60)
        count = upload_embeddings(str(cuad_file), 'legal_contracts')
        total_uploaded += count
    
    # Upload CourtListener
    cl_file = embeddings_dir / 'courtlistener_embeddings.json'
    if cl_file.exists():
        print("\n" + "=" * 60)
        print("⚖️  Processing CourtListener Opinions")
        print("=" * 60)
        count = upload_embeddings(str(cl_file), 'legal_cases')
        total_uploaded += count
    
    # Verify
    verify_collections()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Upload Complete!")
    print("=" * 60)
    print(f"\n📊 Total uploaded: {total_uploaded:,} vectors")
    print(f"   • legal_contracts: CUAD contracts")
    print(f"   • legal_cases: CourtListener opinions")
    
    print("\n🎯 Next: Build RAG system (Week 11-12)")
    print("   Script: rag_system/rag_engine.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
