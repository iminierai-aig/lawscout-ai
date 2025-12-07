# Current LawScout AI Architecture (v2.0)

## Live Production
- URL: https://lawscoutai.com
- Platform: Render
- Framework: Streamlit
- Deployment: Docker (ghcr.io/iminierai-aig/lawscout-ai:v2.0.0)

## Environment Variables (Production)
- QDRANT_URL
- QDRANT_API_KEY
- GEMINI_API_KEY

## Critical Dependencies
- streamlit==1.31.0
- qdrant-client==1.7.0
- google-generativeai==0.3.0
- sentence-transformers==2.3.0

## Traffic Stats (Baseline for Comparison)
- [ ] Document current traffic
- [ ] Document response times
- [ ] Document error rates
- [ ] Document user complaints

## Rollback Contact
- GitHub: [your-username]
- Render Dashboard: https://dashboard.render.com
- Qdrant Dashboard: https://cloud.qdrant.io

## Emergency Rollback Command
```bash
docker pull ghcr.io/iminierai-aig/lawscout-ai:v2.0.0
docker tag ghcr.io/iminierai-aig/lawscout-ai:v2.0.0 \
           ghcr.io/iminierai-aig/lawscout-ai:latest
docker push ghcr.io/iminierai-aig/lawscout-ai:latest
```
# Then trigger Render redeploy