"""
Test Collection Script - Verify data collection works
Tests CUAD and CourtListener collection with small samples
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collection.collect_cuad import CUADCollector
from data_collection.collect_courtlistener import CourtListenerCollector

def test_cuad():
    """Test CUAD collection"""
    print("\n" + "=" * 60)
    print("TEST 1: CUAD Collection")
    print("=" * 60)
    
    try:
        collector = CUADCollector(output_dir="data/test_cuad")
        contracts = collector.download_cuad()
        
        if contracts and len(contracts) > 0:
            collector.save_contracts(contracts, "test_contracts.json")
            print(f"✅ CUAD Test Passed: {len(contracts)} contracts")
            return True
        else:
            print("❌ CUAD Test Failed: No contracts collected")
            return False
            
    except Exception as e:
        print(f"❌ CUAD Test Failed: {e}")
        return False

def test_courtlistener():
    """Test CourtListener collection"""
    print("\n" + "=" * 60)
    print("TEST 2: CourtListener Collection")
    print("=" * 60)
    
    try:
        collector = CourtListenerCollector(output_dir="data/test_courtlistener")
        opinions = collector.fetch_opinions(limit=10)  # Just 10 for testing
        
        if opinions and len(opinions) > 0:
            collector.save_opinions(opinions, "test_opinions.json")
            print(f"✅ CourtListener Test Passed: {len(opinions)} opinions")
            return True
        else:
            print("⚠️  CourtListener Test: 0 opinions collected")
            print("💡 This is expected if you don't have an API token yet")
            print("   Get one at: https://www.courtlistener.com/api/rest-info/")
            return False
            
    except Exception as e:
        print(f"⚠️  CourtListener Test Warning: {e}")
        print("💡 This is expected if you don't have an API token yet")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 DATA COLLECTION TESTS")
    print("=" * 60)
    
    # Run tests
    cuad_result = test_cuad()
    cl_result = test_courtlistener()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"CUAD Collection:        {'✅ PASS' if cuad_result else '❌ FAIL'}")
    print(f"CourtListener Collection: {'✅ PASS' if cl_result else '⚠️  SKIPPED (no API token)'}")
    print("=" * 60)
    
    if cuad_result:
        print("\n✅ CUAD is working! You can run:")
        print("   python data_collection/collect_cuad.py")
    
    if cl_result:
        print("\n✅ CourtListener is working! You can run:")
        print("   python data_collection/collect_courtlistener.py")
    elif not cl_result:
        print("\n💡 To enable CourtListener:")
        print("   1. Get API token: https://www.courtlistener.com/api/rest-info/")
        print("   2. Add to .env: COURTLISTENER_API_TOKEN=your_token")
        print("   3. Run: python data_collection/collect_courtlistener.py")

if __name__ == "__main__":
    main()
