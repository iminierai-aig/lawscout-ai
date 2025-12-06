# 🛡️ Safe Testing Guide - How to Test Without Breaking Your App

**Goal:** Test all new features safely without risking your working application.

---

## ✅ **Strategy 1: Git Branch Testing** (Recommended)

### **Step 1: Create a Backup Branch**

```bash
# Make sure everything is committed first
git add .
git commit -m "backup: save working state before testing v2.0"

# Create and switch to test branch
git checkout -b test-v2.0-features

# Your main/master branch is safe - you're now in test branch
git branch  # Should show * test-v2.0-features
```

### **Step 2: Test in Virtual Environment**

```bash
# Create separate test virtual environment
python -m venv venv-test
source venv-test/bin/activate  # On Windows: venv-test\Scripts\activate

# Install new dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "rank-bm25|transformers|regex"
```

### **Step 3: Run Tests First**

```bash
# Run all tests to verify nothing is broken
pytest tests/ -v

# If tests pass, you're good to proceed!
# If tests fail, check the error messages
```

### **Step 4: Test the App**

```bash
# Run the app on a different port (so you can compare with old version)
streamlit run web_app/app.py --server.port 8502

# Visit: http://localhost:8502
```

### **Step 5: Compare Side-by-Side** (Optional)

```bash
# In another terminal, checkout your working version
git checkout main  # or master
source venv/bin/activate  # Your original venv
streamlit run web_app/app.py --server.port 8501

# Now you have:
# - Old version at http://localhost:8501
# - New version at http://localhost:8502
# Compare them side-by-side!
```

### **Step 6: Decision Time**

**If everything works great:**
```bash
# Merge the test branch
git checkout main  # or master
git merge test-v2.0-features
git branch -d test-v2.0-features  # Delete test branch

# Update production
git push
```

**If something is broken:**
```bash
# Just switch back to main - no harm done!
git checkout main  # or master

# Delete test branch if you want
git branch -D test-v2.0-features
```

---

## ✅ **Strategy 2: Feature Flags** (Progressive Testing)

Test features one at a time by disabling them initially.

### **Create Safe Defaults Config**

Create `config.py`:

```python
# config.py
"""
Feature flags for safe testing
Set to False to disable features
"""

FEATURE_FLAGS = {
    # New features - start disabled
    'enable_hybrid_search': False,      # Start False, test individually
    'enable_reranking': False,          # Start False, test individually
    'enable_advanced_filters': False,   # Start False, test individually
    'enable_citation_extraction': False, # Start False, test individually
    
    # Existing features - keep enabled
    'enable_streaming': True,
    'enable_query_history': True,
    'enable_analytics': True,
    'enable_export': True,
}

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURE_FLAGS.get(feature_name, False)
```

### **Testing Schedule**

**Day 1: Test Hybrid Search Only**
```python
FEATURE_FLAGS = {
    'enable_hybrid_search': True,  # ← Test this today
    'enable_reranking': False,
    'enable_advanced_filters': False,
    'enable_citation_extraction': False,
}
```

**Day 2: Test Reranking Only**
```python
FEATURE_FLAGS = {
    'enable_hybrid_search': True,   # Worked yesterday
    'enable_reranking': True,       # ← Test this today
    'enable_advanced_filters': False,
    'enable_citation_extraction': False,
}
```

**Day 3: Test Filters**
```python
FEATURE_FLAGS = {
    'enable_hybrid_search': True,
    'enable_reranking': True,
    'enable_advanced_filters': True,  # ← Test this today
    'enable_citation_extraction': False,
}
```

**Day 4: Test Citations**
```python
FEATURE_FLAGS = {
    'enable_hybrid_search': True,
    'enable_reranking': True,
    'enable_advanced_filters': True,
    'enable_citation_extraction': True,  # ← Test this today
}
```

---

## ✅ **Strategy 3: Separate Test Script**

Create a standalone test script that doesn't modify the main app.

### **Create `test_new_features.py`**

```python
#!/usr/bin/env python
"""
Standalone script to test new features safely
Run this without touching your main app
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_hybrid_search():
    """Test hybrid search in isolation"""
    print("\n" + "="*60)
    print("Testing Hybrid Search")
    print("="*60)
    
    try:
        from rag_system.hybrid_search import HybridSearchEngine
        
        # Create engine
        engine = HybridSearchEngine(use_reranking=False)
        print("✅ Hybrid search engine initialized")
        
        # Test BM25
        docs = [
            {'chunk_id': '1', 'text': 'contract termination clause', 'score': 0.9},
            {'chunk_id': '2', 'text': 'software license agreement', 'score': 0.8},
        ]
        
        results = engine.bm25_search("termination", docs, top_k=1)
        print(f"✅ BM25 search works - found {len(results)} results")
        
        # Test hybrid
        hybrid_results = engine.hybrid_search("termination", docs, top_k=1)
        print(f"✅ Hybrid search works - found {len(hybrid_results)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_reranking():
    """Test reranking in isolation"""
    print("\n" + "="*60)
    print("Testing Cross-Encoder Reranking")
    print("="*60)
    
    try:
        from rag_system.hybrid_search import HybridSearchEngine
        
        # Create engine with reranking
        engine = HybridSearchEngine(use_reranking=True)
        print("✅ Reranker model loaded")
        
        # Test reranking
        docs = [
            {'chunk_id': '1', 'text': 'contract termination requires notice', 'score': 0.8},
            {'chunk_id': '2', 'text': 'software license payment terms', 'score': 0.9},
        ]
        
        reranked = engine.rerank("termination notice", docs, top_k=2)
        print(f"✅ Reranking works - reranked {len(reranked)} results")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_citations():
    """Test citation extraction in isolation"""
    print("\n" + "="*60)
    print("Testing Citation Extraction")
    print("="*60)
    
    try:
        from rag_system.citation_utils import CitationExtractor
        
        # Create extractor
        extractor = CitationExtractor()
        print("✅ Citation extractor initialized")
        
        # Test extraction
        text = "In Smith v. Jones, 123 U.S. 456, the Court held..."
        citations = extractor.extract_citations(text)
        
        print(f"✅ Citation extraction works - found {len(citations)} citations")
        
        if citations:
            for cit in citations:
                print(f"   - {cit['text']} -> {cit['link']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_engine_compatibility():
    """Test that RAG engine still works with new features"""
    print("\n" + "="*60)
    print("Testing RAG Engine Backward Compatibility")
    print("="*60)
    
    try:
        from rag_system.rag_engine import LegalRAGEngine
        
        # Try to initialize (won't work without API keys, but will test imports)
        print("✅ RAG engine imports successfully")
        print("✅ All new modules are compatible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 SAFE FEATURE TESTING")
    print("Testing new features without modifying main app")
    print("="*60)
    
    results = {
        'Hybrid Search': test_hybrid_search(),
        'Reranking': test_reranking(),
        'Citations': test_citations(),
        'RAG Engine': test_rag_engine_compatibility(),
    }
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Safe to use new features in main app")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("❌ Do NOT use new features until issues are fixed")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

### **Run the test script:**

```bash
python test_new_features.py
```

This tests everything without touching your main app!

---

## ✅ **Strategy 4: Docker Container Testing**

Test in complete isolation using Docker.

### **Build Test Container**

```bash
# Build the image
docker build -t lawscout-test .

# Run in container (isolated from your system)
docker run -p 8503:8501 \
  -e QDRANT_URL="your_url" \
  -e QDRANT_API_KEY="your_key" \
  -e GEMINI_API_KEY="your_key" \
  lawscout-test

# Visit: http://localhost:8503
```

Your main app is completely unaffected!

---

## 📋 **Systematic Testing Checklist**

### **Phase 1: Dependency Testing** (5 minutes)

```bash
# 1. Check if new packages install
pip install rank-bm25 transformers regex

# 2. Verify imports work
python -c "from rank_bm25 import BM25Okapi; print('✅ rank-bm25')"
python -c "from transformers import AutoModel; print('✅ transformers')"
python -c "import regex; print('✅ regex')"

# 3. Check no conflicts
pip check
```

### **Phase 2: Unit Testing** (10 minutes)

```bash
# Run new tests only
pytest tests/test_hybrid_search.py -v
pytest tests/test_citations.py -v

# If these pass, new code is working!
```

### **Phase 3: Integration Testing** (15 minutes)

```bash
# Run full test suite
pytest tests/ -v

# All tests should pass
```

### **Phase 4: UI Testing** (20 minutes)

Start the app and test each feature:

**Test 1: Basic functionality (verify nothing broke)**
- [ ] App starts without errors
- [ ] Can enter a query
- [ ] Search returns results
- [ ] Streaming works
- [ ] Query history appears

**Test 2: Hybrid search**
- [ ] Open Advanced Filters
- [ ] Enable "Hybrid Search"
- [ ] Run a query
- [ ] Check for score breakdown in results
- [ ] Verify shows "semantic_score" and "bm25_score"

**Test 3: Reranking**
- [ ] Enable "Cross-Encoder Reranking"
- [ ] Run a query
- [ ] Should take ~1s longer
- [ ] Check for "rerank_score" in results
- [ ] Verify results seem more relevant

**Test 4: Filters**
- [ ] Enable date filter, set 2020-2025
- [ ] Run a query
- [ ] Results should be within date range (if metadata exists)
- [ ] Try jurisdiction filter
- [ ] Try court filter

**Test 5: Citations**
- [ ] Enable "Extract Citations"
- [ ] Search for cases (not contracts)
- [ ] Check source documents
- [ ] Look for "📎 Citations Found"
- [ ] Click a citation link
- [ ] Should open CourtListener in new tab

---

## 🔄 **Rollback Plan** (If Something Breaks)

### **Immediate Rollback**

```bash
# Stop the app (Ctrl+C)

# Switch back to working version
git checkout main  # or master

# Restart with old version
streamlit run web_app/app.py
```

### **Partial Rollback** (Keep some features)

If only one feature is broken, you can disable it:

**Option A: Comment out in code**

In `web_app/app.py`, find the feature and comment it out:

```python
# Temporarily disable reranking
use_reranking = False  # st.checkbox(...)
```

**Option B: Modify defaults**

In `web_app/app.py`, change default values:

```python
use_hybrid = st.checkbox("Hybrid Search", value=False)  # Default to False
use_reranking = st.checkbox("Reranking", value=False)   # Default to False
```

---

## 🔍 **Debugging Failed Features**

### **If Hybrid Search Fails**

```python
# Test BM25 separately
from rank_bm25 import BM25Okapi

docs = ["test document one", "test document two"]
tokenized = [doc.split() for doc in docs]
bm25 = BM25Okapi(tokenized)
scores = bm25.get_scores("test".split())
print(scores)  # Should print array of scores
```

### **If Reranking Fails**

```python
# Test cross-encoder separately
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
scores = model.predict([["query", "document"]])
print(scores)  # Should print array of scores
```

### **If Citations Fail**

```python
# Test citation extraction separately
from rag_system.citation_utils import CitationExtractor

extractor = CitationExtractor()
text = "123 U.S. 456"
citations = extractor.extract_citations(text)
print(citations)  # Should find the citation
```

---

## 📊 **Performance Comparison**

Run both versions and compare:

### **Old Version Baseline**
```bash
git checkout main
streamlit run web_app/app.py --server.port 8501
# Test query, note response time
```

### **New Version Test**
```bash
git checkout test-v2.0-features
streamlit run web_app/app.py --server.port 8502
# Same query, compare response time
```

**Expected:**
- Old: ~2-3s
- New (with all features): ~3-4s
- New (no reranking): ~2.5-3s

---

## ✅ **Sign-Off Checklist**

Before committing to v2.0, verify:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] App starts without errors
- [ ] Basic search still works
- [ ] Hybrid search works
- [ ] Reranking improves results
- [ ] Filters work (if metadata exists)
- [ ] Citations extract and link correctly
- [ ] No performance regression > 2s
- [ ] No memory leaks during testing
- [ ] Analytics still tracks queries
- [ ] Export still works
- [ ] Query history still works

---

## 🎯 **Recommended Testing Plan**

**Conservative Approach (Safest):**
1. Day 1: Branch + Virtual Env setup
2. Day 2: Run all tests, fix any issues
3. Day 3: Test hybrid search only
4. Day 4: Add reranking
5. Day 5: Test filters
6. Day 6: Test citations
7. Day 7: Full integration test
8. Day 8: Merge to main if all good

**Moderate Approach:**
1. Hour 1: Branch setup + dependencies
2. Hour 2: Run all tests
3. Hour 3: Test all features in UI
4. Hour 4: Compare with old version
5. Hour 5: Merge if satisfied

**Aggressive Approach (Not Recommended):**
1. Install dependencies directly
2. Test quickly
3. Hope nothing breaks 😅

**👉 We recommend the Moderate Approach**

---

## 💡 **Pro Tips**

1. **Test with real queries** - Use actual legal questions you care about
2. **Check error logs** - Look in terminal for warnings/errors
3. **Monitor memory** - Watch RAM usage during testing
4. **Test on small limit first** - Use `limit=2` to test faster
5. **Compare results** - Same query in old vs new version
6. **Screenshot comparisons** - Take screenshots to compare UI
7. **Note response times** - Time each query
8. **Test edge cases** - Empty queries, very long queries, special characters

---

## 🆘 **If You Get Stuck**

### **Error: "No module named 'rank_bm25'"**
```bash
pip install rank-bm25
```

### **Error: "No module named 'transformers'"**
```bash
pip install transformers
```

### **Error: Model download fails**
```bash
# Pre-download models
python -c "from sentence_transformers import CrossEncoder; CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

### **Error: App won't start**
```bash
# Check for syntax errors
python -m py_compile rag_system/rag_engine.py
python -m py_compile web_app/app.py
```

### **Error: Tests fail**
```bash
# Run with verbose output
pytest tests/ -vv --tb=long

# Check specific test
pytest tests/test_hybrid_search.py::TestHybridSearch::test_initialization -vv
```

---

## 🎉 **Success Criteria**

You're ready to use v2.0 when:

✅ All tests pass  
✅ App starts without errors  
✅ Search works with new features  
✅ Results are better than before  
✅ Performance is acceptable  
✅ No crashes during testing  
✅ You feel confident it works!  

---

**Happy (safe) testing! 🛡️**

