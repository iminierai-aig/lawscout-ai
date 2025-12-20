# LawScout AI - Core Principles & Development Priorities

## 🎯 Mission Statement

**Make LawScout AI the most relevant, organized, truthful, and citation-useful legal research tool on the internet for its price point.**

---

## 🏆 Core Principles (Priority Order)

### 1. **Search Relevance** ⭐⭐⭐⭐⭐
**Highest Priority - This is what brings users back**

- **State-Specific Prioritization**: When users mention a state (Florida, California, etc.), prioritize and boost state-specific cases, courts, and legal principles
- **Query Understanding**: Detect legal concepts, jurisdictions, case types, and context from natural language queries
- **Result Ranking**: Use hybrid search (semantic + BM25) with intelligent reranking to surface the most relevant results first
- **Score Boosting**: Intelligently boost results that match:
  - State/jurisdiction mentioned in query
  - Court level (state vs federal)
  - Case type (criminal, civil, contract, etc.)
  - Date relevance (recent cases when appropriate)
- **Filtering**: Remove low-relevance results (negative scores, off-topic content)

**Implementation Checklist:**
- [x] State-specific query detection
- [x] State-specific result boosting (15% score boost)
- [x] Result sorting by relevance
- [ ] Query expansion for legal terms
- [ ] Multi-jurisdiction handling
- [ ] Temporal relevance (recent cases for evolving law)

---

### 2. **Organization & Presentation** ⭐⭐⭐⭐⭐
**Critical for User Experience**

- **Clear Metadata**: Every result must have:
  - Case name (not "Unknown")
  - Citation (properly formatted, clickable)
  - Court (extracted from text if not in metadata)
  - Date (year extracted from citations)
  - URL (CourtListener link when citation available)
- **Structured Results**: 
  - Grouped by relevance
  - Clear visual hierarchy
  - Expandable source details
  - Citation links that work
- **Answer Quality**:
  - Well-organized paragraphs
  - Clear source attribution
  - Logical flow of information

**Implementation Checklist:**
- [x] Enhanced metadata extraction (case names, citations, courts, dates)
- [x] CourtListener URL construction
- [x] Citation extraction from text
- [ ] Result grouping by topic/court
- [ ] Visual result cards with better hierarchy
- [ ] Export functionality improvements

---

### 3. **Truthfulness & Accuracy** ⭐⭐⭐⭐⭐
**Non-negotiable for legal research**

- **Source Attribution**: Always cite sources accurately
- **Honest Limitations**: When results don't match query (e.g., no Florida-specific cases), clearly state that
- **No Hallucination**: LLM responses must be grounded in provided sources
- **Citation Verification**: Ensure citations are real and linkable
- **Context Preservation**: Don't take quotes out of context

**Implementation Checklist:**
- [x] Source attribution in answers
- [x] Clear statements when state-specific results aren't available
- [ ] Citation validation
- [ ] Source verification checks
- [ ] Context window management to prevent truncation

---

### 4. **Citation Usefulness** ⭐⭐⭐⭐
**Essential for legal professionals**

- **Proper Citation Format**: Extract and display citations in standard legal format
- **Clickable Links**: All citations should link to CourtListener or original source
- **Multiple Citations**: Extract all citations from a document, not just the first
- **Citation Context**: Show where citations appear in the text
- **CourtListener Integration**: Automatically construct CourtListener URLs from citations

**Implementation Checklist:**
- [x] Citation extraction from text (multiple patterns)
- [x] CourtListener URL construction
- [x] Citation display in results
- [ ] Citation validation (verify they exist)
- [ ] Citation type detection (case, statute, regulation)
- [ ] Citation ranking by relevance

---

### 5. **Cost Efficiency** ⭐⭐⭐
**Enables sustainable low pricing**

- **Token Optimization**: Minimize LLM input/output tokens
- **Context Window Management**: Limit to top 3-5 most relevant chunks
- **Caching**: Cache frequent queries
- **Smart Prompting**: Concise, focused prompts
- **Usage Tracking**: Monitor costs and set limits

**Implementation Checklist:**
- [x] Context window optimization (top 3 chunks, 8000 char limit)
- [x] Concise prompts (40% token reduction)
- [x] Query result caching
- [x] Usage tracking and cost limits
- [ ] More aggressive caching strategies
- [ ] Prompt compression techniques

---

## 🚀 Continuous Improvement Areas

### Search Quality
- [ ] Query expansion (synonyms, legal terms)
- [ ] Multi-query understanding (compound questions)
- [ ] Negative query handling ("not", "excluding")
- [ ] Temporal queries ("recent", "latest", "2024")

### Metadata Extraction
- [ ] Better case name extraction (handle abbreviations)
- [ ] Party name extraction (plaintiff/defendant)
- [ ] Judge name extraction
- [ ] Topic classification

### Result Presentation
- [ ] Result clustering by topic
- [ ] Timeline visualization for cases
- [ ] Court hierarchy visualization
- [ ] Related cases suggestions

### Citation Enhancement
- [ ] Citation network (cases citing this case)
- [ ] Citation frequency analysis
- [ ] Overruled/superseded detection
- [ ] Parallel citations

---

## 📊 Success Metrics

Track these metrics to measure improvement:

1. **Relevance Score**: Average relevance score of top 3 results
2. **State Match Rate**: % of state-specific queries that return state-specific results
3. **Metadata Completeness**: % of results with complete metadata (name, citation, court, date)
4. **Citation Accuracy**: % of citations that link correctly
5. **User Satisfaction**: Search success rate (users finding what they need)
6. **Cost per Query**: Average cost per search query

---

## 🎯 Development Guidelines

When working on LawScout AI, always ask:

1. **Does this improve search relevance?**
   - Will users find more relevant results?
   - Are we prioritizing the right information?

2. **Does this improve organization?**
   - Is information clearly presented?
   - Can users quickly find what they need?

3. **Does this improve truthfulness?**
   - Are we being honest about limitations?
   - Are sources accurately attributed?

4. **Does this improve citation usefulness?**
   - Are citations properly formatted?
   - Do links work correctly?

5. **Does this maintain cost efficiency?**
   - Can we deliver this at our price point?
   - Are we optimizing token usage?

---

## 📝 Notes for Future Development

- **Always prioritize relevance over quantity** - Better to return 3 highly relevant results than 10 mediocre ones
- **State-specific queries are common** - Always check for state mentions and prioritize accordingly
- **Citations are critical** - Legal professionals need accurate, linkable citations
- **Metadata matters** - "Unknown" is not acceptable - extract from text if needed
- **Honesty builds trust** - If results don't match query, say so clearly
- **Cost control enables low pricing** - Every optimization helps maintain competitive pricing

---

**Last Updated**: December 2024  
**Status**: Active Development  
**Priority**: Search Relevance > Organization > Truthfulness > Citations > Cost Efficiency

