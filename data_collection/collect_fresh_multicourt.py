"""
Fresh CourtListener Collection - Multiple Courts
Fixed version with proper API calls per court
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

class CourtCollector:
    def __init__(self):
        self.headers = {
            'Authorization': f'Token {API_TOKEN}',
            'User-Agent': 'LawScout-AI/3.0'
        }
        self.output_dir = Path('data/courtlistener')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_court(self, court_code, target, description):
        """Collect opinions from a specific court"""
        print(f"\n{'='*70}")
        print(f"📋 {description} ({court_code})")
        print(f"   Target: {target:,} opinions")
        print(f"{'='*70}\n")
        
        opinions = []
        url = f"{BASE_URL}?court={court_code}&order_by=-date_created"
        
        with tqdm(total=target, desc=court_code.upper(), unit="opinions") as pbar:
            while len(opinions) < target and url:
                try:
                    response = requests.get(url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        
                        for result in results:
                            if len(opinions) >= target:
                                break
                            
                            opinion = {
                                'id': result.get('id'),
                                'court': court_code,  # Use actual court from parameter
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
                    
                    elif response.status_code in [429, 502, 503]:
                        wait = 60 if response.status_code == 429 else 30
                        print(f"\n⚠️  Error {response.status_code}, waiting {wait}s...")
                        time.sleep(wait)
                        continue
                    
                    else:
                        print(f"\n❌ Error {response.status_code}")
                        break
                
                except Exception as e:
                    print(f"\n❌ Error: {e}")
                    time.sleep(10)
                    continue
        
        # Save to individual file
        output_file = self.output_dir / f"opinions_{court_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(opinions, f, indent=2, ensure_ascii=False)
        
        size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"\n✅ Collected {len(opinions):,} from {court_code.upper()}")
        print(f"💾 Saved to {output_file.name} ({size_mb:.2f} MB)\n")
        
        return opinions

def main():
    print("="*70)
    print("🚀 LawScout AI - Fresh Multi-Court Collection")
    print("="*70)
    
    collector = CourtCollector()
    
    # Collection plan - realistic targets based on API availability
    courts = [
        ('scotus', 2160, 'Supreme Court'),
        ('ca9', 5000, '9th Circuit'),
        ('ca2', 4000, '2nd Circuit'),
        ('cadc', 3000, 'DC Circuit'),
        ('ca5', 2500, '5th Circuit'),
        ('ca11', 2340, '11th Circuit'),
        ('ca1', 3000, '1st Circuit'),
        ('ca4', 3000, '4th Circuit'),
        ('ca6', 3000, '6th Circuit'),
    ]
    
    all_opinions = []
    
    for court_code, target, description in courts:
        opinions = collector.collect_court(court_code, target, description)
        all_opinions.extend(opinions)
        print(f"📊 Total collected so far: {len(all_opinions):,}\n")
    
    # Save combined file
    combined_file = collector.output_dir / "opinions_all_combined.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump(all_opinions, f, indent=2, ensure_ascii=False)
    
    size_mb = combined_file.stat().st_size / (1024 * 1024)
    
    print("="*70)
    print("✅ COLLECTION COMPLETE!")
    print("="*70)
    print(f"\n📊 Total opinions: {len(all_opinions):,}")
    print(f"💾 Combined file: {size_mb:.2f} MB")
    print(f"📁 Location: {combined_file}")
    
    # Breakdown by court
    courts_count = {}
    for op in all_opinions:
        court = op.get('court', 'unknown')
        courts_count[court] = courts_count.get(court, 0) + 1
    
    print(f"\n📊 Breakdown by court:")
    for court, count in sorted(courts_count.items()):
        print(f"   {court}: {count:,} opinions")
    
    print("\n🎯 Next: python preprocessing/clean_documents.py")
    print("="*70)

if __name__ == "__main__":
    main()
