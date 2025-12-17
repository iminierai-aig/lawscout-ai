"""
CUAD Dataset Collection - Working Version
Downloads from official sources: HuggingFace, Zenodo, or creates sample dataset
"""
import json
import os
from pathlib import Path
import requests
from typing import Dict, List
from tqdm import tqdm

class CUADCollector:
    """Collect CUAD (Contract Understanding Atticus Dataset) contracts"""
    
    def __init__(self, output_dir: str = "data/cuad"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Multiple download sources (in order of preference)
        self.sources = [
            {
                "name": "HuggingFace (theatticusproject)",
                "url": "https://huggingface.co/datasets/theatticusproject/cuad/resolve/main/CUAD_v1.json",
                "format": "json"
            },
            {
                "name": "Zenodo (Official Release)",
                "url": "https://zenodo.org/records/4595826/files/CUAD_v1.json",
                "format": "json"
            }
        ]
    
    def download_from_source(self, source: Dict) -> List[Dict]:
        """Try downloading from a specific source"""
        print(f"📥 Trying {source['name']}...")
        print(f"   URL: {source['url']}")
        
        try:
            response = requests.get(source['url'], timeout=300, stream=True)
            response.raise_for_status()
            
            # Get total size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            # Download with progress bar
            content = b""
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    content += chunk
                    pbar.update(len(chunk))
            
            # Parse JSON
            data = json.loads(content.decode('utf-8'))
            
            # Handle different JSON structures
            if isinstance(data, dict):
                if 'data' in data:
                    contracts = data['data']
                elif 'paragraphs' in data:
                    contracts = self.parse_squad_format(data)
                else:
                    # Assume it's a single contract
                    contracts = [data]
            else:
                contracts = data
            
            print(f"✅ Downloaded {len(contracts)} contracts from {source['name']}")
            return contracts
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed: {e}")
            return []
    
    def parse_squad_format(self, data: Dict) -> List[Dict]:
        """Parse SQuAD-formatted CUAD data"""
        contracts = []
        
        if 'data' in data:
            for document in data['data']:
                for paragraph in document.get('paragraphs', []):
                    context = paragraph.get('context', '')
                    for qa in paragraph.get('qas', []):
                        contracts.append({
                            'id': qa.get('id', ''),
                            'context': context,
                            'question': qa.get('question', ''),
                            'answers': qa.get('answers', []),
                            'is_impossible': qa.get('is_impossible', False)
                        })
        
        return contracts
    
    def download_cuad(self) -> List[Dict]:
        """Try downloading CUAD from multiple sources"""
        print("=" * 60)
        print("🔍 Searching for CUAD Dataset...")
        print("=" * 60)
        
        # Try each source in order
        for source in self.sources:
            contracts = self.download_from_source(source)
            if contracts:
                return contracts
        
        # If all sources fail, try HuggingFace datasets API
        print("\n💡 Trying HuggingFace datasets library...")
        contracts = self.try_huggingface_datasets()
        if contracts:
            return contracts
        
        # Last resort: create sample dataset
        print("\n⚠️  All sources failed. Creating sample dataset...")
        return self.create_sample_dataset()
    
    def try_huggingface_datasets(self) -> List[Dict]:
        """Try loading from HuggingFace datasets library"""
        try:
            from datasets import load_dataset
            
            # Try the official repository
            print("📥 Loading from HuggingFace datasets...")
            dataset = load_dataset("theatticusproject/cuad")
            
            contracts = []
            for split in dataset.keys():
                for item in dataset[split]:
                    contracts.append(dict(item))
            
            print(f"✅ Loaded {len(contracts)} contracts from HuggingFace")
            return contracts
            
        except Exception as e:
            print(f"❌ HuggingFace datasets failed: {e}")
            return []
    
    def create_sample_dataset(self) -> List[Dict]:
        """Create a sample contract dataset for testing"""
        print("📝 Creating sample contract dataset...")
        print("💡 This is for testing only. For production, download real CUAD data.")
        
        sample_contracts = [
            {
                "id": f"sample_{i}",
                "title": title,
                "context": context,
                "question": question,
                "answers": {"text": [answer], "answer_start": [context.find(answer)]},
                "metadata": {
                    "source": "sample",
                    "contract_type": contract_type,
                    "parties": ["Party A", "Party B"]
                }
            }
            for i, (title, context, question, answer, contract_type) in enumerate([
                (
                    "Software License Agreement",
                    "This Software License Agreement ('Agreement') is entered into as of January 1, 2024, "
                    "by and between TechCorp Inc. ('Licensor') and UserCompany LLC ('Licensee'). "
                    "The Licensor grants to Licensee a non-exclusive, non-transferable license to use the Software "
                    "for a term of five (5) years. The license fee shall be $50,000 per year, payable annually in advance.",
                    "What is the license term?",
                    "five (5) years",
                    "software_license"
                ),
                (
                    "Service Agreement",
                    "This Service Agreement is made effective as of February 15, 2024, between ServicePro Inc. "
                    "('Provider') and ClientCorp ('Client'). Provider agrees to provide consulting services "
                    "for a period of three (3) years at a rate of $150 per hour. Payment terms are Net 30 days.",
                    "What is the hourly rate?",
                    "$150 per hour",
                    "service_agreement"
                ),
                (
                    "Non-Disclosure Agreement",
                    "This Non-Disclosure Agreement ('NDA') is executed on March 1, 2024, by and between "
                    "InnovateTech LLC ('Disclosing Party') and PartnerCo Inc. ('Receiving Party'). "
                    "The Receiving Party agrees to maintain confidentiality for a period of two (2) years "
                    "following the termination of this agreement.",
                    "What is the confidentiality period?",
                    "two (2) years",
                    "nda"
                ),
                (
                    "Partnership Agreement",
                    "This Partnership Agreement is entered into on April 10, 2024, between Alpha Ventures "
                    "and Beta Holdings. The partnership shall continue for an initial term of ten (10) years, "
                    "with automatic renewal unless terminated. Profits and losses shall be shared equally.",
                    "What is the initial partnership term?",
                    "ten (10) years",
                    "partnership"
                ),
                (
                    "Employment Contract",
                    "This Employment Agreement is effective as of May 1, 2024, between MegaCorp Inc. ('Employer') "
                    "and John Doe ('Employee'). The Employee is hired as Senior Developer at an annual salary "
                    "of $120,000. The employment term is indefinite, subject to termination provisions. "
                    "The Employee is entitled to 20 days of paid vacation per year.",
                    "What is the annual salary?",
                    "$120,000",
                    "employment"
                ),
                (
                    "Lease Agreement",
                    "This Commercial Lease Agreement is dated June 1, 2024, between Property Owner LLC ('Landlord') "
                    "and Retail Store Inc. ('Tenant'). The lease term shall be seven (7) years commencing on July 1, 2024. "
                    "Monthly rent is $8,000, payable on the first day of each month.",
                    "What is the monthly rent?",
                    "$8,000",
                    "lease"
                ),
                (
                    "Purchase Agreement",
                    "This Asset Purchase Agreement is entered into on July 15, 2024, between Seller Co. and Buyer Inc. "
                    "The purchase price for all assets is $2,500,000, payable in three installments over 18 months. "
                    "Closing shall occur within sixty (60) days of the execution of this agreement.",
                    "What is the total purchase price?",
                    "$2,500,000",
                    "purchase"
                ),
                (
                    "Distribution Agreement",
                    "This Distribution Agreement is effective August 1, 2024, between Manufacturer LLC ('Supplier') "
                    "and Distributor Corp. ('Distributor'). The exclusive distribution rights are granted for "
                    "a territory covering the Western United States for an initial term of five (5) years.",
                    "What territory is covered?",
                    "Western United States",
                    "distribution"
                ),
                (
                    "Franchise Agreement",
                    "This Franchise Agreement is dated September 1, 2024, between FranchiseCo Inc. ('Franchisor') "
                    "and Franchisee LLC ('Franchisee'). The initial franchise fee is $75,000, with an ongoing "
                    "royalty of 6% of gross sales. The franchise term is twelve (12) years.",
                    "What is the initial franchise fee?",
                    "$75,000",
                    "franchise"
                ),
                (
                    "Consulting Agreement",
                    "This Consulting Agreement is executed on October 1, 2024, between Expert Advisors Inc. "
                    "('Consultant') and StartupCo ('Client'). The Consultant shall provide strategic advisory "
                    "services for a fixed monthly fee of $10,000 for a period of one (1) year.",
                    "What is the monthly consulting fee?",
                    "$10,000",
                    "consulting"
                )
            ])
        ]
        
        print(f"✅ Created {len(sample_contracts)} sample contracts")
        print("   Includes: Software License, Services, NDA, Partnership, Employment, etc.")
        return sample_contracts
    
    def save_contracts(self, contracts: List[Dict], filename: str = "contracts.json"):
        """Save contracts to JSON file"""
        output_file = self.output_dir / filename
        
        print(f"\n💾 Saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(contracts, f, indent=2, ensure_ascii=False)
        
        file_size = output_file.stat().st_size
        print(f"✅ Saved {len(contracts)} contracts ({file_size / 1024:.1f} KB)")
        
        return output_file
    
    def collect_all(self):
        """Main collection workflow"""
        print("\n" + "=" * 60)
        print("📋 CUAD Contract Collection")
        print("=" * 60)
        
        # Download contracts
        contracts = self.download_cuad()
        
        # Save to file
        output_file = self.save_contracts(contracts)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Collection Complete!")
        print("=" * 60)
        print(f"📊 Total Contracts: {len(contracts)}")
        print(f"📁 Output File: {output_file}")
        print(f"💾 File Size: {output_file.stat().st_size / (1024*1024):.2f} MB")
        
        # Show sample
        if contracts:
            print(f"\n📝 Sample Contract:")
            sample = contracts[0]
            print(f"   ID: {sample.get('id', 'N/A')}")
            print(f"   Context: {str(sample.get('context', ''))[:100]}...")
            print(f"   Question: {sample.get('question', 'N/A')}")
        
        print("=" * 60)
        
        return output_file

def main():
    collector = CUADCollector()
    collector.collect_all()

if __name__ == "__main__":
    main()
