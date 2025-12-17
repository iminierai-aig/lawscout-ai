"""
CourtListener Data Collection - Scale to 7 GB
Collects from multiple federal courts to maximize Qdrant storage
"""

import os
import json
import requests
import time
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('COURTLISTENER_API_TOKEN')
BASE_URL = "https://www.courtlistener.com/api/rest/v4/opinions/"

class MultiCourtCollector:
    def __init__(self):
        self.headers = {
            'Authorization': f'Token {API_TOKEN}',
            'User-Agent': 'LawScout-AI/2.0'
        }
        self.output_dir = Path('data/courtlistener')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_court(self, court_code, limit, description):
        """Collect opinions from a specific court"""
        print(f"\n{'='*70}")
        print(f"📋 Collecting from {description} ({court_code})")
        print(f"   Target: {limit:,} opinions")
        print(f"{'='*70}\n")
        
        opinions = []
        url = f"{BASE_URL}?court={court_code}&order_by=-date_created"
        
        with tqdm(total=limit, desc=f"{court_code.upper()}", unit="opinions") as pbar:
            while len(opinions) < limit and url:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        
                        for result in results:
                            if len(opinions) >= limit:
                                break
                            
                            opinion = {
                                'id': result.get('id'),
                                'court': court_code,
                                'date_created': result.get('date_created'),
                                'case_name': result.get('case_name', 'Unknown'),
                                'text': result.get('plain_text', ''),
                                'download_url': result.get('download_url', ''),
                                'author_str': result.get('author_str', ''),
                                'type': result.get('type', '')
                            }
                            
                            if opinion['text']:
                                opinions.append(opinion)
                                pbar.update(1)
                        
                        url = data.get('next')
                        time.sleep(0.5)
                    
                    elif response.status_code == 429:
                        print(f"\n⚠️  Rate limited. Waiting 60 seconds...")
                        time.sleep(60)
                        continue
                    
                    else:
                        print(f"\n❌ Error {response.status_code}: {response.text[:200]}")
                        break
                
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    time.sleep(5)
                    continue
        
        print(f"\n✅ Collected {len(opinions):,} opinions from {court_code.upper()}")
        return opinions
    
    def save_opinions(self, opinions, filename):
        """Save opinions to JSON"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(opinions, f, indent=2, ensure_ascii=False)
        
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"💾 Saved to {filepath} ({size_mb:.2f} MB)")
        return size_mb

def collect_option_a_quick():
    """Option A: Quick Fill - Priority Courts"""
    print("\n" + "="*70)
    print("🎯 OPTION A: QUICK FILL (PRIORITY COURTS)")
    print("="*70)
    print("\nTarget: ~19,000 opinions → 7.4 GB total")
    print("Time: 4-5 hours")
    print("Courts: SCOTUS, 9th, 2nd, DC, 5th, 11th Circuits\n")
    
    collector = MultiCourtCollector()
    
    collection_plan = [
        ('scotus', 2160, 'Supreme Court (complete)'),
        ('ca9', 5000, '9th Circuit (largest)'),
        ('ca2', 4000, '2nd Circuit (NY/financial)'),
        ('cadc', 3000, 'DC Circuit (admin law)'),
        ('ca5', 2500, '5th Circuit (TX/oil-gas)'),
        ('ca11', 2340, '11th Circuit (FL/diverse)')
    ]
    
    all_opinions = []
    
    for court, limit, description in collection_plan:
        opinions = collector.collect_from_court(court, limit, description)
        all_opinions.extend(opinions)
        collector.save_opinions(opinions, f"opinions_{court}.json")
    
    print(f"\n{'='*70}")
    print("💾 Saving combined file...")
    combined_size = collector.save_opinions(all_opinions, 'opinions_all_courts.json')
    
    print(f"\n{'='*70}")
    print("✅ COLLECTION COMPLETE!")
    print(f"{'='*70}")
    print(f"\n📊 Summary:")
    print(f"   Total opinions: {len(all_opinions):,}")
    print(f"   Total size: {combined_size:.2f} MB (~{combined_size/1024:.2f} GB)")
    print(f"\n🎯 Next: python preprocessing/clean_documents.py")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    print("="*70)
    print("�� LawScout AI - Scale Up Data Collection")
    print("="*70)
    print("\nOption A: Quick Fill (Priority Courts) - 19K opinions, 7.4 GB, 4-5 hours\n")
    
    confirm = input("Start collection? (yes/no): ").strip().lower()
    if confirm == 'yes':
        collect_option_a_quick()
    else:
        print("❌ Collection cancelled")
