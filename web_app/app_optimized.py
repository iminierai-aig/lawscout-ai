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

# Initialize session state for quick search
if "query" not in st.session_state:
    st.session_state.query = ""

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
        with st.spinner(f"🔍 Searching {limit} documents across {collection}..."):
                try:
                    # Use ask() method which combines search + answer generation
                    results = rag.ask(
                        query=query,
                        collection_type=collection,
                        limit=limit,
                        return_sources=show_sources
                    )
                    
                    # Display AI Answer
                    st.markdown("---")
                    st.markdown("### 💡 Answer")
                    st.info(results['answer'])
                    
                    # Display Sources
                    if show_sources and results.get('sources'):
                        st.markdown("---")
                        st.markdown("### 📚 Sources")
                        
                        for i, doc in enumerate(results['sources'], 1):
                            relevance = doc.get('score', 0)
                            title = doc.get('source', 'Untitled Document')
                            collection_name = doc.get('collection', 'Unknown')
                            text_content = doc.get('text', '')
                            
                            with st.expander(
                                f"📄 **Source {i}:** {title[:80]}... ({relevance:.1%} relevance)",
                                expanded=(i == 1)
                            ):
                                st.markdown(f"**Collection:** `{collection_name}`")
                                st.markdown(f"**Relevance Score:** {relevance:.2%}")
                                st.markdown("**Content:**")
                                st.text_area(
                                    "Document excerpt",
                                    value=text_content[:1000] + "..." if len(text_content) > 1000 else text_content,
                                    height=200,
                                    disabled=True,
                                    label_visibility="collapsed"
                                )
                    
                    # Display Metrics
                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
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

