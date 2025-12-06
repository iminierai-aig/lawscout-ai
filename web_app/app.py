import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.rag_engine import LegalRAGEngine

# Page config
st.set_page_config(page_title="LawScout AI", page_icon="⚖️", layout="wide")

# Initialize RAG engine
@st.cache_resource
def get_rag_engine():
    return LegalRAGEngine()

rag = get_rag_engine()

# Initialize session state
if "query" not in st.session_state:
    st.session_state.query = ""
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "current_results" not in st.session_state:
    st.session_state.current_results = None

# ========== SIDEBAR ==========
# Permanent red warning banner at top
st.sidebar.markdown(
    """
    <div style="background-color: #ff3b30; padding: 10px; border-radius: 10px; color: white; font-weight: bold; text-align: center;">
    ⚠️ RESEARCH DEMO ONLY – NOT LEGAL ADVICE – VERIFY ALL SOURCES
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("")  # Add spacing

st.sidebar.markdown("### ⚖️ LawScout AI")
st.sidebar.markdown("*AI-Powered Legal Research Assistant*")
st.sidebar.markdown("---")

# ========== EXAMPLE QUERIES (Expandable) ==========
st.sidebar.markdown("### 💡 Example Queries")

with st.sidebar.expander("📄 Contract Analysis"):
    st.markdown("""
    • Warranty provisions in commercial agreements  
    • Termination clauses in software licenses  
    • Confidentiality obligations in NDAs  
    • Payment terms and milestones  
    • Dispute resolution mechanisms  
    """)

with st.sidebar.expander("⚖️ Intellectual Property"):
    st.markdown("""
    • IP rights transfer in contracts  
    • Patent licensing terms  
    • Trademark usage restrictions  
    • Copyright assignment clauses  
    • Trade secret protection  
    """)

with st.sidebar.expander("🛡️ Liability & Risk"):
    st.markdown("""
    • Indemnification provisions  
    • Limitations of liability  
    • Force majeure clauses  
    • Insurance requirements  
    • Warranty disclaimers  
    """)

with st.sidebar.expander("📚 Case Law Research"):
    st.markdown("""
    • Patent infringement precedents  
    • Contract breach remedies  
    • Employment discrimination cases  
    • Securities fraud litigation  
    • Antitrust violations  
    """)

with st.sidebar.expander("🔀 Cross-Domain Queries"):
    st.markdown("""
    • Software licensing + patent cases  
    • Employment contracts + discrimination law  
    • M&A agreements + securities regulations  
    • Service agreements + consumer protection  
    """)

st.sidebar.markdown("---")

# ========== QUERY HISTORY ==========
if st.session_state.query_history:
    with st.sidebar.expander("📜 Query History", expanded=False):
        for i, hist_query in enumerate(reversed(st.session_state.query_history[-10:])):
            if st.button(f"🔄 {hist_query[:40]}...", key=f"hist_{i}", use_container_width=True):
                st.session_state.query = hist_query
                st.rerun()

st.sidebar.markdown("---")

# ========== QUICK SEARCH BUTTONS ==========
st.sidebar.markdown("### 🚀 Quick Search")

# Row 1
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("☠️ Termination", use_container_width=True):
        st.session_state.query = "What are termination clauses in software licenses?"
        st.rerun()
    if st.button("💰 Payment", use_container_width=True):
        st.session_state.query = "What are payment terms and conditions?"
        st.rerun()
    if st.button("📋 Warranties", use_container_width=True):
        st.session_state.query = "What are warranty provisions in commercial agreements?"
        st.rerun()

with col2:
    if st.button("🧠 IP Rights", use_container_width=True):
        st.session_state.query = "How are intellectual property rights transferred?"
        st.rerun()
    if st.button("⚠️ Liability", use_container_width=True):
        st.session_state.query = "What are limitations of liability?"
        st.rerun()
    if st.button("🛡️ Indemnity", use_container_width=True):
        st.session_state.query = "What are indemnification provisions?"
        st.rerun()

st.sidebar.markdown("---")

# ========== SETTINGS ==========
with st.sidebar.expander("⚙️ Settings", expanded=True):
    collection = st.radio(
        "Search in:",
        ["both", "contracts", "cases"],
        format_func=lambda x: {
            "both": "📋 Contracts & Cases",
            "contracts": "📄 Contracts Only",
            "cases": "⚖️ Cases Only"
        }[x],
        help="Choose which document collection to search"
    )
    
    limit = st.slider(
        "Number of Results:",
        min_value=1,
        max_value=10,
        value=5,
        help="How many relevant documents to return"
    )
    
    show_sources = st.checkbox(
        "Show Source Documents",
        value=True,
        help="Display full source document excerpts"
    )

# ========== ADVANCED FILTERS ==========
with st.sidebar.expander("🔍 Advanced Filters", expanded=False):
    st.markdown("**Search Methods:**")
    
    use_hybrid = st.checkbox(
        "Hybrid Search (Semantic + Keyword)",
        value=True,
        help="Combines semantic understanding with keyword matching (BM25)"
    )
    
    use_reranking = st.checkbox(
        "Cross-Encoder Reranking",
        value=True,
        help="Uses advanced model to rerank results for better relevance"
    )
    
    extract_citations = st.checkbox(
        "Extract Citations",
        value=True,
        help="Automatically extract and link legal citations"
    )
    
    st.markdown("---")
    st.markdown("**Date Range (Cases Only):**")
    st.info("ℹ️ Filters require indexed metadata. Currently disabled until data has these fields.")
    
    use_date_filter = st.checkbox("Enable Date Filter", value=False, disabled=True)
    
    if use_date_filter:
        col1, col2 = st.columns(2)
        with col1:
            start_year = st.number_input("From Year", min_value=1900, max_value=2025, value=2000)
        with col2:
            end_year = st.number_input("To Year", min_value=1900, max_value=2025, value=2025)
        date_range = (f"{start_year}-01-01", f"{end_year}-12-31")
    else:
        date_range = None
    
    st.markdown("---")
    st.markdown("**Jurisdiction (Cases Only):**")
    
    jurisdiction = st.selectbox(
        "Select Jurisdiction",
        ["All", "Federal", "California", "New York", "Texas", "Florida"],
        help="Filter by legal jurisdiction",
        disabled=True
    )
    
    jurisdiction = None  # Disabled for now
    
    st.markdown("---")
    st.markdown("**Court Level (Cases Only):**")
    
    court_level = st.selectbox(
        "Select Court",
        ["All", "Supreme Court", "Circuit Court", "District Court", "State Supreme Court"],
        help="Filter by court level",
        disabled=True
    )
    
    court_level = None  # Disabled for now

st.sidebar.markdown("---")

# ========== SYSTEM STATUS ==========
st.sidebar.markdown("### 📊 System Status")
col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Documents", "5,511")
    st.metric("Chunks", "171,813")
with col2:
    st.metric("Courts", "6")
    st.metric("Vectors", "384-dim")

# Analytics Summary
analytics = rag.get_analytics()
if analytics:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Session Stats")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Queries", len(analytics))
    with col2:
        avg_time = sum(a.get('total_time', 0) for a in analytics) / len(analytics)
        st.metric("Avg Time", f"{avg_time:.2f}s")

st.sidebar.markdown("---")

# ========== MAIN CONTENT ==========
# Title at top of main content
st.title("⚖️ LawScout AI")
st.markdown("*AI-Powered Legal Research Assistant*")
st.markdown("📊 1,511 documents | 240,633 chunks | 384-dimensional embeddings")
st.markdown("⚠️ *For research purposes only. Not legal advice.*")
st.markdown("---")

# Search Interface with session state integration
query = st.text_input(
    "🔍 Enter your legal research question:",
    value=st.session_state.query,
    placeholder="E.g., What are the key provisions in software license agreements?",
    help="Ask questions in natural language about legal contracts and case law"
)

# Update session state when user types
if query != st.session_state.query:
    st.session_state.query = query

# Search button
search_clicked = st.button("🔎 Search", type="primary", use_container_width=True)

# Search button logic
if search_clicked:
    if query:
        # Add to query history
        if query not in st.session_state.query_history:
            st.session_state.query_history.append(query)
        
        with st.spinner(f"🔍 Searching {limit} documents across {collection}..."):
                try:
                    # Build filters dictionary
                    filters = {}
                    if date_range:
                        filters['date_range'] = date_range
                    if jurisdiction:
                        filters['jurisdiction'] = jurisdiction
                    if court_level:
                        filters['court'] = court_level
                    
                    # Use ask() method with all advanced features
                    results = rag.ask(
                        query=query,
                        collection_type=collection,
                        limit=limit,
                        return_sources=show_sources,
                        stream=True,  # Enable streaming
                        filters=filters if filters else None,
                        use_hybrid=use_hybrid,
                        use_reranking=use_reranking,
                        extract_citations=extract_citations
                    )
                    
                    # Store results in session state
                    st.session_state.current_results = results
                    
                    # Display AI Answer with Streaming
                    st.markdown("---")
                    st.markdown("### 💡 Answer")
                    
                    answer_placeholder = st.empty()
                    full_answer = ""
                    
                    # Stream the answer with error handling
                    try:
                        for chunk in results['answer']:
                            full_answer += chunk
                            answer_placeholder.info(full_answer + "▌")
                        
                        # Final answer without cursor
                        answer_placeholder.info(full_answer)
                    except Exception as stream_error:
                        # Handle streaming errors gracefully
                        if full_answer:
                            # Show partial answer if we got some content
                            answer_placeholder.warning(full_answer + f"\n\n⚠️ Streaming interrupted: {str(stream_error)}")
                        else:
                            # Show error if no content received
                            answer_placeholder.error(f"❌ Streaming error: {str(stream_error)}")
                            full_answer = f"Error during streaming: {str(stream_error)}"
                    
                    # Update results with full answer for later use
                    results['answer'] = full_answer
                    
                    # Display Sources with Enhanced Information
                    if show_sources and results.get('sources'):
                        st.markdown("---")
                        st.markdown("### 📚 Sources")
                        
                        for i, doc in enumerate(results['sources'], 1):
                            relevance = doc.get('score', 0)
                            title = doc.get('source', 'Untitled Document')
                            collection_name = doc.get('collection', 'Unknown')
                            text_content = doc.get('text', '')
                            
                            # Build title with score details
                            score_details = []
                            if 'rerank_score' in doc:
                                score_details.append(f"Rerank: {doc['rerank_score']:.1%}")
                            if 'semantic_score' in doc:
                                score_details.append(f"Semantic: {doc['semantic_score']:.1%}")
                            if 'bm25_score' in doc:
                                score_details.append(f"BM25: {doc['bm25_score']:.2f}")
                            
                            score_info = " | ".join(score_details) if score_details else f"{relevance:.1%} relevance"
                            
                            with st.expander(
                                f"📄 **Source {i}:** {title[:60]}... ({score_info})",
                                expanded=(i == 1)
                            ):
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.markdown(f"**Collection:** `{collection_name}`")
                                with col2:
                                    st.markdown(f"**Final Score:** {relevance:.2%}")
                                
                                # Show score breakdown if available
                                if score_details:
                                    st.markdown("**Score Breakdown:**")
                                    score_cols = st.columns(3)
                                    if 'rerank_score' in doc:
                                        score_cols[0].metric("Rerank", f"{doc['rerank_score']:.1%}")
                                    if 'semantic_score' in doc:
                                        score_cols[1].metric("Semantic", f"{doc['semantic_score']:.1%}")
                                    if 'bm25_score' in doc:
                                        score_cols[2].metric("BM25", f"{doc['bm25_score']:.2f}")
                                
                                # Display citations if extracted
                                if 'citations' in doc and doc['citations']:
                                    st.markdown("**📎 Citations Found:**")
                                    for cit in doc['citations']:
                                        if cit.get('link'):
                                            st.markdown(f"- [{cit['text']}]({cit['link']}) (CourtListener)")
                                        else:
                                            st.markdown(f"- {cit['text']}")
                                
                                st.markdown("**Content:**")
                                st.text_area(
                                    "Document excerpt",
                                    value=text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                                    height=200,
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                    
                    # Display Metrics with Performance Data
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "Documents Searched",
                            "171,813",
                            help="Total chunks in vector database"
                        )
                    with col2:
                        st.metric(
                            "Relevant Sources",
                            results.get('num_sources', len(results.get('sources', []))),
                            help="Number of relevant documents found"
                        )
                    with col3:
                        if results.get('sources'):
                            top_score = results['sources'][0].get('score', 0)
                            st.metric(
                                "Top Match Score",
                                f"{top_score:.1%}",
                                help="Relevance of best match"
                            )
                        else:
                            st.metric("Top Match Score", "N/A")
                    with col4:
                        search_time = results.get('search_time', 0)
                        st.metric(
                            "Search Time",
                            f"{search_time:.2f}s",
                            help="Vector search latency"
                        )
                    
                    # Export functionality
                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        # Create exportable content
                        export_content = f"""# LawScout AI Research Results
                        
Query: {query}
Date: {results.get('search_time', 'N/A')}
Collection: {collection}

## Answer
{full_answer}

## Sources
"""
                        if results.get('sources'):
                            for i, source in enumerate(results['sources'], 1):
                                export_content += f"\n### Source {i}\n"
                                export_content += f"Title: {source.get('source', 'Unknown')}\n"
                                export_content += f"Relevance: {source.get('score', 0):.2%}\n"
                                export_content += f"Content: {source.get('text', '')}\n"
                        
                        st.download_button(
                            label="📥 Export Results",
                            data=export_content,
                            file_name=f"lawscout_research_{query[:30].replace(' ', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                            
                except Exception as e:
                    st.error(f"❌ Search error: {str(e)}")
                    st.info("💡 Try rephrasing your question or check system status.")
                    import traceback
                    st.code(traceback.format_exc())
    else:
        st.warning("⚠️ Please enter a search query or use Quick Search buttons.")

# Ethical & Legal Notices
st.markdown("---")
st.markdown("### ⚖️ LawScout AI – Ethical & Legal Notices")
st.markdown("""
- This is a **research demonstration only** – not legal advice.

- All answers are generated by AI and may contain errors.

- Always verify with primary sources and consult qualified attorneys.

- Data sources: Public domain court opinions (CourtListener / Free Law Project) + anonymized contracts (CUAD dataset).

- No personally identifiable information is stored or processed.

- Built for educational and research purposes under fair use / public domain principles.
""")

# Data Attribution at bottom
st.markdown("---")
st.markdown("### 📚 Data Attribution")
st.markdown("""
Legal case opinions sourced from [CourtListener](https://www.courtlistener.com/), a project of the non-profit [Free Law Project](https://free.law/).

Contract data from the [CUAD Dataset](https://www.atticusprojectai.org/cuad).

We are grateful for their mission to make legal information freely accessible.
""")


# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Dark theme enhancements */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Quick search buttons */
    .stButton>button {
        background-color: #262730;
        border: 1px solid #4a4a5e;
        border-radius: 8px;
        padding: 8px 12px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #ff4b4b;
        border-color: #ff4b4b;
        color: white;
        transform: translateY(-2px);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #262730;
        border-radius: 8px;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #ff4b4b;
    }
    
    /* Search button */
    .stButton>button[kind="primary"] {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

