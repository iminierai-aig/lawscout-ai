"""
CourtListener API Collection - Fixed with Authentication
Downloads legal opinions with proper API token handling
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CourtListenerCollector:
    """Collect legal opinions from CourtListener API with authentication"""
    
    def __init__(self, output_dir: str = "data/courtlistener", api_token: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get API token from parameter or environment
        self.api_token = api_token or os.getenv('COURTLISTENER_API_TOKEN')
        
        self.base_url = "https://www.courtlistener.com/api/rest/v4"
        
        # Set up headers with authentication
        self.headers = {
            'User-Agent': 'LawScout-AI/1.0 (Educational Research Project)',
        }
        
        if self.api_token:
            self.headers['Authorization'] = f'Token {self.api_token}'
            print(f"✅ Using API token: {self.api_token[:8]}...")
        else:
            print("⚠️  No API token found - using rate-limited access")
            print("💡 Get a free token at: https://www.courtlistener.com/api/rest-info/")
        
        self.batch_size = 20  # Fetch 20 at a time
        self.delay = 2 if self.api_token else 5  # Slower rate without token
    
    def fetch_opinions(self, limit: int = 100000, court: str = "scotus") -> List[Dict]:
        """
        Fetch opinions from CourtListener API
        
        Args:
            limit: Maximum number of opinions to fetch
            court: Court identifier (scotus, ca9, etc.)
        """
        print(f"📥 Fetching opinions from CourtListener...")
        print(f"🎯 Target: {limit} opinions from '{court}' court")
        
        all_opinions = []
        next_url = f"{self.base_url}/opinions/?court={court}&order_by=-date_created"
        
        with tqdm(total=limit, desc="Downloading") as pbar:
            while len(all_opinions) < limit and next_url:
                try:
                    # Make request
                    response = requests.get(next_url, headers=self.headers, timeout=30)
                    
                    if response.status_code == 401:
                        print("\n❌ Authentication failed!")
                        print("💡 To fix this:")
                        print("   1. Visit: https://www.courtlistener.com/sign-in/")
                        print("   2. Create a free account")
                        print("   3. Get your API token from: https://www.courtlistener.com/api/rest-info/")
                        print("   4. Add to .env file:")
                        print("      COURTLISTENER_API_TOKEN=your_token_here")
                        return all_opinions
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract opinions
                    results = data.get('results', [])
                    all_opinions.extend(results)
                    
                    # Update progress
                    pbar.update(len(results))
                    
                    # Get next page
                    next_url = data.get('next')
                    
                    # Rate limiting
                    time.sleep(self.delay)
                    
                    # Stop if we have enough
                    if len(all_opinions) >= limit:
                        break
                    
                except requests.exceptions.RequestException as e:
                    print(f"\n⚠️  Request failed: {e}")
                    
                    if "429" in str(e):
                        print("⏸️  Rate limit hit - waiting 60 seconds...")
                        time.sleep(60)
                    else:
                        break
        
        # Trim to exact limit
        all_opinions = all_opinions[:limit]
        
        print(f"✅ Collected {len(all_opinions)} opinions")
        return all_opinions
    
    def save_opinions(self, opinions: List[Dict], filename: str = "opinions_scotus.json"):
        """Save opinions to JSON file"""
        output_file = self.output_dir / filename
        
        print(f"💾 Saving to {output_file}...")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(opinions, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(opinions)} opinions")
        return output_file
    
    def collect_all(self, limit: int = 100000):
        """Main collection workflow"""
        print("=" * 60)
        print("CourtListener Opinion Collection - Starting")
        print("=" * 60)
        
        # Fetch opinions
        opinions = self.fetch_opinions(limit=limit)
        
        if not opinions:
            print("\n❌ No opinions collected")
            print("💡 Check your API token and try again")
            return None
        
        # Save to file
        output_file = self.save_opinions(opinions)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ CourtListener Collection Complete!")
        print(f"📊 Total Opinions: {len(opinions)}")
        print(f"📁 Output: {output_file}")
        print(f"💾 Size: {output_file.stat().st_size / (1024*1024):.2f} MB")
        print("=" * 60)
        
        return output_file

def main():
    # Try to collect 100K opinions
    collector = CourtListenerCollector()
    collector.collect_all(limit=100000)

if __name__ == "__main__":
    main()
