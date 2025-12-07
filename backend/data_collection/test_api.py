import sys
from pathlib import Path

# Add parent directory to path so we can import
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collection.collect_courtlistener import CourtListenerCollector
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Test the API token first
api_token = os.getenv('COURTLISTENER_API_TOKEN')
print(f'🔍 Testing API token: {api_token[:8]}...')
print()

# Try different endpoints (using V4 for new users)
endpoints = [
    'https://www.courtlistener.com/api/rest/v4/search/',
    'https://www.courtlistener.com/api/rest/v4/clusters/',
    'https://www.courtlistener.com/api/rest/v4/dockets/',
    'https://www.courtlistener.com/api/rest/v4/opinions/',
]

headers = {
    'Authorization': f'Token {api_token}',
    'User-Agent': 'LawScout-AI/1.0'
}

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        print(f'{endpoint}')
        print(f'  Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Results: {data.get("count", "N/A")} items')
            print(f'  ✅ This endpoint works!')
        else:
            print(f'  ❌ Error: {response.text[:100]}')
        print()
    except Exception as e:
        print(f'  ❌ Exception: {e}')
        print()

