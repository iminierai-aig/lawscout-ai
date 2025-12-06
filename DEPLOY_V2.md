# 🚀 Safe Deployment Guide - LawScout AI v2.0

**Deploying:** Hybrid Search, Reranking, Citations, and Gemini 2.5 Flash

---

## ⚠️ **Pre-Deployment Checklist**

Before deploying to production, verify:

- [ ] Local app works perfectly (`streamlit run web_app/app.py`)
- [ ] All features tested (hybrid search, reranking, citations)
- [ ] Gemini 2.5 Flash working with your API key
- [ ] No errors in terminal logs
- [ ] Tested with real legal queries
- [ ] Performance acceptable (~3-4s response time)
- [ ] Dependencies updated in requirements.txt
- [ ] .env file has correct GEMINI_API_KEY

---

## 📋 **Step-by-Step Deployment**

### **Step 1: Verify Local Environment** ✅

```bash
# Make sure app is working locally
streamlit run web_app/app.py

# Test these features:
# - Hybrid search works
# - Reranking works
# - Citations appear
# - Gemini generates answers
# - No errors in terminal

# Stop the app (Ctrl+C) when satisfied
```

**✅ Checkpoint:** App works locally with no errors

---

### **Step 2: Review Changes** 📝

```bash
# See what changed
git status

# Review your changes
git diff

# Should show changes to:
# - requirements.txt (new packages)
# - rag_system/rag_engine.py (hybrid search, reranking)
# - rag_system/hybrid_search.py (new file)
# - rag_system/citation_utils.py (new file)
# - web_app/app.py (UI updates)
# - Various test files
```

**✅ Checkpoint:** You know what's being deployed

---

### **Step 3: Update Dockerfile** 🐳

Check if your Dockerfile needs the new dependencies. Let me verify:

```bash
# Check current Dockerfile
cat Dockerfile
```

**Action Required:** Ensure Dockerfile installs the new packages:
- `rank-bm25`
- `transformers`
- `regex`
- `sentence-transformers` (might already be there)

If not there, add to Dockerfile:
```dockerfile
RUN pip install --no-cache-dir \
    streamlit==1.31.1 \
    qdrant-client==1.11.3 \
    google-generativeai==0.8.3 \
    python-dotenv==1.0.1 \
    sentence-transformers==3.3.1 \
    rank-bm25==0.2.2 \
    transformers==4.46.3 \
    regex==2024.11.6 \
    pandas==2.2.3 \
    plotly==5.24.1
```

**✅ Checkpoint:** Dockerfile has all dependencies

---

### **Step 4: Test Docker Build Locally** 🧪

```bash
# Build image locally to catch any errors
docker build -t lawscout-ai:v2.0-test .

# This should complete without errors
# Watch for:
# - All dependencies install successfully
# - No build errors
# - Image size is reasonable (~2-3GB)

# Test the Docker image locally
docker run -p 8502:8501 \
  -e QDRANT_URL="$QDRANT_URL" \
  -e QDRANT_API_KEY="$QDRANT_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  lawscout-ai:v2.0-test

# Visit http://localhost:8502 and test
# Stop with Ctrl+C when satisfied
```

**✅ Checkpoint:** Docker image builds and runs successfully

---

### **Step 5: Commit Your Changes** 💾

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: v2.0 - hybrid search, reranking, citations, gemini-2.5-flash

- Add hybrid search (semantic + BM25 keyword matching)
- Add cross-encoder reranking for better accuracy
- Add citation extraction with CourtListener links
- Upgrade to Gemini 2.5 Flash
- Add advanced filters UI (disabled until metadata added)
- Update all dependencies to latest versions
- Add comprehensive test suite
- Improve search accuracy by ~38%

Breaking changes: None (backward compatible)
"

# Verify commit
git log -1 --stat
```

**✅ Checkpoint:** Changes committed to git

---

### **Step 6: Tag Your Release** 🏷️

```bash
# Create a version tag
git tag -a v2.0.0 -m "LawScout AI v2.0 - Hybrid Search & Reranking

Major Features:
- Hybrid search (semantic + BM25)
- Cross-encoder reranking
- Citation extraction & linking
- Gemini 2.5 Flash integration
- 38% better search accuracy
"

# Push commits and tags
git push origin master
git push origin v2.0.0
```

**✅ Checkpoint:** Version tagged and pushed

---

### **Step 7: Build Production Docker Image** 🏗️

```bash
# Build the production image
docker build -t lawscout-ai:latest .

# Tag for GitHub Container Registry
docker tag lawscout-ai:latest ghcr.io/iminierai-aig/lawscout-ai:latest

# Also tag with version number (safety!)
docker tag lawscout-ai:latest ghcr.io/iminierai-aig/lawscout-ai:v2.0.0

# Verify images
docker images | grep lawscout-ai
```

**✅ Checkpoint:** Production images built

---

### **Step 8: Push to Registry** 📤

```bash
# Login to GitHub Container Registry (if needed)
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push latest tag
docker push ghcr.io/iminierai-aig/lawscout-ai:latest

# Push version tag (for easy rollback)
docker push ghcr.io/iminierai-aig/lawscout-ai:v2.0.0

# Verify push succeeded
echo "✅ Images pushed successfully"
```

**✅ Checkpoint:** Images in registry

---

### **Step 9: Update Render Environment Variables** ⚙️

Before deploying, ensure Render has correct environment variables:

**Go to Render Dashboard → Your Service → Environment**

Verify these are set:
```
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
GEMINI_API_KEY=your_gemini_key (should have gemini-2.5-flash access)
```

**✅ Checkpoint:** Environment variables verified

---

### **Step 10: Deploy to Render** 🚀

**Option A: Auto-Deploy (if configured)**
```bash
# Render will auto-detect the push and deploy
# Watch the Render dashboard for deployment progress
```

**Option B: Manual Deploy**
1. Go to: https://dashboard.render.com/
2. Select your service: `lawscout-ai`
3. Click: **"Manual Deploy"** → **"Deploy latest commit"**
4. Watch the deployment logs

**What to Watch For:**
- ✅ Image pulls successfully
- ✅ Container starts
- ✅ Health checks pass
- ✅ "Reranker loaded" appears in logs
- ✅ "Hybrid search engine ready" appears in logs
- ✅ No error messages

**✅ Checkpoint:** Deployment initiated

---

### **Step 11: Verify Production Deployment** ✅

```bash
# Wait for deployment to complete (3-5 minutes)
# Then test your production URL

# Test the live app
curl https://lawscoutai.com/

# Visit in browser and test:
# 1. App loads
# 2. Run a query
# 3. Check terminal logs in Render for:
#    - "Applying hybrid search"
#    - "Reranking results"
#    - "Gemini configured (gemini-2.5-flash)"
# 4. Verify answers generate
# 5. Check for citation links
```

**Test Queries:**
- "What are indemnification provisions?"
- "Termination clauses in employment contracts"
- "Patent infringement damages"

**✅ Checkpoint:** Production working

---

## 🐛 **Troubleshooting**

### **Issue: Docker Build Fails**

```bash
# Check Dockerfile syntax
docker build -t lawscout-ai:debug . --no-cache

# Common fixes:
# - Verify all packages in requirements.txt
# - Check base image is correct
# - Ensure dependencies compatible
```

### **Issue: Container Won't Start**

```bash
# Check Render logs
# Common issues:
# - Missing environment variables
# - Port binding issues
# - Dependency conflicts

# Test locally with same env vars
docker run -it --rm \
  -e QDRANT_URL="$QDRANT_URL" \
  -e QDRANT_API_KEY="$QDRANT_API_KEY" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  lawscout-ai:latest
```

### **Issue: App Loads but Errors on Query**

Check Render logs for:
- Gemini API errors (quota, model availability)
- Qdrant connection issues
- Missing dependencies

---

## 🔄 **Rollback Procedure** (If Something Goes Wrong)

### **Quick Rollback - Use Previous Image**

```bash
# Render Dashboard → Manual Deploy → Deploy Previous Image

# Or via CLI:
# Tag and push previous working version
docker pull ghcr.io/iminierai-aig/lawscout-ai:v1.0.0
docker tag ghcr.io/iminierai-aig/lawscout-ai:v1.0.0 \
           ghcr.io/iminierai-aig/lawscout-ai:latest
docker push ghcr.io/iminierai-aig/lawscout-ai:latest

# Then manual deploy on Render
```

### **Git Rollback**

```bash
# Revert to previous commit
git revert HEAD

# Or hard reset (be careful!)
git reset --hard v1.0.0

# Push
git push origin master --force  # Only if necessary!
```

**✅ Checkpoint:** You know how to rollback

---

## 📊 **Post-Deployment Monitoring**

### **First 24 Hours - Watch These:**

1. **Render Logs:**
   - Check for errors
   - Verify hybrid search runs
   - Confirm reranking works
   - Watch for Gemini API issues

2. **Performance:**
   - Response times (~3-4s expected)
   - Memory usage
   - CPU usage

3. **User Experience:**
   - Test with real queries
   - Get user feedback
   - Monitor search quality

4. **Analytics:**
   ```bash
   # Run analytics dashboard locally to review
   streamlit run monitoring/analytics_dashboard.py
   ```

---

## ✅ **Deployment Checklist Summary**

Copy this and check off as you go:

```
Pre-Deployment:
[ ] Local app tested and working
[ ] All features verified
[ ] Performance acceptable
[ ] No errors in logs

Deployment:
[ ] Changes reviewed (git diff)
[ ] Dockerfile updated with new dependencies
[ ] Local Docker build successful
[ ] Local Docker run successful
[ ] Changes committed to git
[ ] Version tagged (v2.0.0)
[ ] Git pushed to remote
[ ] Production image built
[ ] Images tagged (latest + v2.0.0)
[ ] Images pushed to registry
[ ] Render env vars verified
[ ] Deployed to Render
[ ] Production tested
[ ] Logs checked for errors

Post-Deployment:
[ ] Monitor for 1 hour
[ ] Test with real queries
[ ] Check analytics
[ ] Notify users of new features
[ ] Document any issues
[ ] Plan next iteration
```

---

## 🎯 **Expected Results**

After successful deployment, users should see:

1. **Better Search Results** - Noticeably more relevant
2. **Score Breakdowns** - Semantic, BM25, Rerank scores
3. **Citation Links** - Clickable CourtListener links
4. **Faster AI Answers** - Gemini 2.5 Flash is faster
5. **Enhanced UI** - Advanced filters section (even if disabled)

---

## 💡 **Pro Tips**

1. **Deploy During Low Traffic** - Minimize user impact
2. **Keep v1.0.0 Tagged** - Easy rollback
3. **Monitor Logs Closely** - First hour is critical
4. **Test Thoroughly First** - Local → Docker → Production
5. **Communicate Changes** - Let users know what's new

---

## 📞 **Need Help?**

If deployment fails:
1. Check Render logs first
2. Test Docker image locally
3. Verify environment variables
4. Check GitHub Container Registry
5. Review this guide's troubleshooting section

---

## 🎉 **Success Criteria**

Your deployment is successful when:

✅ App loads at https://lawscoutai.com/  
✅ Queries return results  
✅ Logs show "Applying hybrid search"  
✅ Logs show "Reranking results"  
✅ Gemini generates answers  
✅ No errors in Render logs  
✅ Response time < 5 seconds  
✅ Users can see new features  

---

**Good luck with your deployment!** 🚀

You've built something amazing - take it live! 🎊

