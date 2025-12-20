# LawScout AI Development Hints

## 🎯 CRITICAL: Core Development Priorities

When working on LawScout AI, always prioritize in this order:

1. **Search Relevance** - This is what brings users back
   - State-specific query detection and result boosting
   - Intelligent ranking and filtering
   - Query understanding and expansion

2. **Organization & Presentation** - Critical for UX
   - Complete metadata (no "Unknown" titles)
   - Proper citations with working links
   - Clear, structured results

3. **Truthfulness** - Non-negotiable for legal research
   - Honest about limitations
   - Accurate source attribution
   - No hallucination

4. **Citation Usefulness** - Essential for legal professionals
   - Proper citation format
   - Clickable CourtListener links
   - Multiple citations per document

5. **Cost Efficiency** - Enables low pricing
   - Token optimization
   - Smart caching
   - Usage tracking

## 🚨 Always Remember

- **"Unknown" is not acceptable** - Extract metadata from text if needed
- **State-specific queries are common** - Always check and prioritize
- **Citations must be linkable** - Construct CourtListener URLs
- **Honesty builds trust** - Say when results don't match query
- **Relevance over quantity** - 3 great results > 10 mediocre ones

See `docs/CORE_PRINCIPLES.md` for full development guidelines.

