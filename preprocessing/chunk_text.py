"""
Text Chunking Module
Splits legal documents into semantic chunks for embeddings
"""
import json
import re
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

class TextChunker:
    """Chunk legal documents into smaller pieces"""
    
    def __init__(
        self,
        input_dir: str = "data/processed",
        output_dir: str = "data/chunks",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.chunk_size = chunk_size  # characters per chunk
        self.chunk_overlap = chunk_overlap  # overlap between chunks
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split on periods followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_text(self, text: str, doc_id: str) -> List[Dict]:
        """Chunk text into overlapping pieces"""
        if not text:
            return []
        
        chunks = []
        sentences = self.split_into_sentences(text)
        
        current_chunk = ""
        current_sentences = []
        
        for sentence in sentences:
            # If adding this sentence exceeds chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'sentences': current_sentences.copy()
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                current_sentences = [sentence]
            else:
                current_chunk += " " + sentence
                current_sentences.append(sentence)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'sentences': current_sentences
            })
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk.update({
                'chunk_id': f"{doc_id}_chunk_{i:04d}",
                'doc_id': doc_id,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'length': len(chunk['text'])
            })
        
        return chunks
    
    def chunk_cuad(self) -> List[Dict]:
        """Chunk CUAD contracts"""
        input_file = self.input_dir / "cuad_cleaned.json"
        
        if not input_file.exists():
            print(f"❌ CUAD file not found: {input_file}")
            return []
        
        print(f"📋 Chunking CUAD contracts from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        
        all_chunks = []
        for contract in tqdm(contracts, desc="CUAD Chunking"):
            chunks = self.chunk_text(contract['text'], contract['id'])
            
            # Add contract metadata to each chunk
            for chunk in chunks:
                chunk.update({
                    'source': 'CUAD',
                    'filename': contract.get('filename', ''),
                    'num_pages': contract.get('num_pages', 0),
                    'document_type': 'contract'
                })
            
            all_chunks.extend(chunks)
        
        print(f"✅ Created {len(all_chunks)} chunks from {len(contracts)} contracts")
        return all_chunks
    
    def chunk_courtlistener(self) -> List[Dict]:
        """Chunk CourtListener opinions"""
        input_file = self.input_dir / "courtlistener_cleaned.json"
        
        if not input_file.exists():
            print(f"❌ CourtListener file not found: {input_file}")
            return []
        
        print(f"⚖️  Chunking CourtListener opinions from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            opinions = json.load(f)
        
        all_chunks = []
        for opinion in tqdm(opinions, desc="CourtListener Chunking"):
            chunks = self.chunk_text(opinion['text'], opinion['id'])
            
            # Add opinion metadata to each chunk
            for chunk in chunks:
                chunk.update({
                    'source': 'CourtListener',
                    'case_name': opinion.get('case_name', ''),
                    'court': opinion.get('court', 'scotus'),
                    'date_filed': opinion.get('date_filed', ''),
                    'document_type': 'legal_opinion'
                })
            
            all_chunks.extend(chunks)
        
        print(f"✅ Created {len(all_chunks)} chunks from {len(opinions)} opinions")
        return all_chunks
    
    def save_chunks(self, chunks: List[Dict], filename: str):
        """Save chunks to file"""
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"💾 Saved to {output_file} ({file_size:.2f} MB)")
        
        return output_file
    
    def chunk_all(self):
        """Chunk all documents"""
        print("\n" + "=" * 60)
        print("✂️  Text Chunking Pipeline")
        print("=" * 60)
        print(f"⚙️  Chunk size: {self.chunk_size} chars")
        print(f"⚙️  Overlap: {self.chunk_overlap} chars")
        print("=" * 60)
        
        # Chunk CUAD
        cuad_chunks = self.chunk_cuad()
        if cuad_chunks:
            self.save_chunks(cuad_chunks, "cuad_chunks.json")
        
        # Chunk CourtListener
        cl_chunks = self.chunk_courtlistener()
        if cl_chunks:
            self.save_chunks(cl_chunks, "courtlistener_chunks.json")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Chunking Complete!")
        print("=" * 60)
        print(f"📊 CUAD: {len(cuad_chunks)} chunks")
        print(f"📊 CourtListener: {len(cl_chunks)} chunks")
        print(f"📊 Total: {len(cuad_chunks) + len(cl_chunks)} chunks")
        print("=" * 60)
        
        # Statistics
        all_chunks = cuad_chunks + cl_chunks
        if all_chunks:
            avg_length = sum(c['length'] for c in all_chunks) // len(all_chunks)
            print(f"\n📊 Chunk Statistics:")
            print(f"   Average length: {avg_length:,} chars")
            print(f"   Smallest: {min(c['length'] for c in all_chunks):,} chars")
            print(f"   Largest: {max(c['length'] for c in all_chunks):,} chars")
        
        print("\n🎯 Next Step: Generate embeddings (Week 7-8)")
        print("   Use Google Colab for FREE GPU!")
        print("   Script: embeddings/generate_embeddings_local.py")

def main():
    chunker = TextChunker(
        chunk_size=1000,      # 1000 characters per chunk
        chunk_overlap=200     # 200 character overlap
    )
    chunker.chunk_all()

if __name__ == "__main__":
    main()
