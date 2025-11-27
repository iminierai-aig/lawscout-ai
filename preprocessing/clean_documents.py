"""
Document Cleaning Module
Cleans and normalizes legal documents from CUAD and CourtListener
"""
import json
import re
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

class DocumentCleaner:
    """Clean and normalize legal documents"""
    
    def __init__(self, input_dir: str = "data", output_dir: str = "data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def clean_text(self, text: str) -> str:
        """Clean a single text string"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep legal punctuation
        # Keep: periods, commas, semicolons, colons, quotes, parentheses, hyphens
        text = re.sub(r'[^\w\s\.,;:\'"()\-§$%]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Remove excessive dots (e.g., "......")
        text = re.sub(r'\.{4,}', '...', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def clean_cuad(self) -> List[Dict]:
        """Clean CUAD contracts"""
        input_file = self.input_dir / "cuad" / "contracts.json"
        
        if not input_file.exists():
            print(f"❌ CUAD file not found: {input_file}")
            return []
        
        print(f"📋 Cleaning CUAD contracts from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            contracts = json.load(f)
        
        cleaned = []
        for contract in tqdm(contracts, desc="CUAD"):
            cleaned_contract = {
                'id': contract.get('id', ''),
                'source': 'CUAD',
                'filename': contract.get('filename', ''),
                'text': self.clean_text(contract.get('text', '')),
                'num_pages': contract.get('num_pages', 0),
                'original_length': contract.get('length', 0),
                'cleaned_length': len(self.clean_text(contract.get('text', '')))
            }
            
            # Only keep if we have text
            if cleaned_contract['text']:
                cleaned.append(cleaned_contract)
        
        print(f"✅ Cleaned {len(cleaned)}/{len(contracts)} CUAD contracts")
        return cleaned
    
    def clean_courtlistener(self) -> List[Dict]:
        """Clean CourtListener opinions"""
        input_file = self.input_dir / "courtlistener" / "opinions_scotus.json"
        
        if not input_file.exists():
            print(f"❌ CourtListener file not found: {input_file}")
            return []
        
        print(f"⚖️  Cleaning CourtListener opinions from {input_file}...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            opinions = json.load(f)
        
        cleaned = []
        for opinion in tqdm(opinions, desc="CourtListener"):
            # Extract text from different possible fields
            text = ''
            if isinstance(opinion, dict):
                text = opinion.get('plain_text', '') or \
                       opinion.get('html', '') or \
                       opinion.get('text', '') or \
                       str(opinion.get('absolute_url', ''))
            
            cleaned_opinion = {
                'id': str(opinion.get('id', '')),
                'source': 'CourtListener',
                'case_name': opinion.get('case_name', ''),
                'court': opinion.get('court', 'scotus'),
                'date_filed': str(opinion.get('date_filed', '')),
                'text': self.clean_text(text),
                'original_length': len(text),
                'cleaned_length': len(self.clean_text(text))
            }
            
            # Only keep if we have text
            if cleaned_opinion['text']:
                cleaned.append(cleaned_opinion)
        
        print(f"✅ Cleaned {len(cleaned)}/{len(opinions)} CourtListener opinions")
        return cleaned
    
    def save_cleaned(self, data: List[Dict], filename: str):
        """Save cleaned documents"""
        output_file = self.output_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"💾 Saved to {output_file} ({file_size:.2f} MB)")
        
        return output_file
    
    def clean_all(self):
        """Clean all documents"""
        print("\n" + "=" * 60)
        print("🧹 Document Cleaning Pipeline")
        print("=" * 60)
        
        # Clean CUAD
        cuad_cleaned = self.clean_cuad()
        if cuad_cleaned:
            self.save_cleaned(cuad_cleaned, "cuad_cleaned.json")
        
        # Clean CourtListener
        cl_cleaned = self.clean_courtlistener()
        if cl_cleaned:
            self.save_cleaned(cl_cleaned, "courtlistener_cleaned.json")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Cleaning Complete!")
        print("=" * 60)
        print(f"📊 CUAD: {len(cuad_cleaned)} contracts")
        print(f"📊 CourtListener: {len(cl_cleaned)} opinions")
        print(f"📊 Total: {len(cuad_cleaned) + len(cl_cleaned)} documents")
        print("=" * 60)
        
        # Statistics
        if cuad_cleaned:
            avg_cuad = sum(d['cleaned_length'] for d in cuad_cleaned) // len(cuad_cleaned)
            print(f"\n📋 CUAD Stats:")
            print(f"   Average length: {avg_cuad:,} chars")
            print(f"   Smallest: {min(d['cleaned_length'] for d in cuad_cleaned):,} chars")
            print(f"   Largest: {max(d['cleaned_length'] for d in cuad_cleaned):,} chars")
        
        if cl_cleaned:
            avg_cl = sum(d['cleaned_length'] for d in cl_cleaned) // len(cl_cleaned)
            print(f"\n⚖️  CourtListener Stats:")
            print(f"   Average length: {avg_cl:,} chars")
            print(f"   Smallest: {min(d['cleaned_length'] for d in cl_cleaned):,} chars")
            print(f"   Largest: {max(d['cleaned_length'] for d in cl_cleaned):,} chars")
        
        print("\n🎯 Next Step: Run chunking")
        print("   uv run preprocessing/chunk_text.py")

def main():
    cleaner = DocumentCleaner()
    cleaner.clean_all()

if __name__ == "__main__":
    main()
