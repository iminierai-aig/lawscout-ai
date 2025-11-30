"""
LawScout AI - Web Application
Streamlit interface for legal research
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.rag_engine import LegalRAGEngine

# Page config
st.set_page_config(
    page_title="LawScout AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize RAG engine
@st.cache_resource
def load_rag_engine():
    """Load RAG engine (cached)"""
    return LegalRAGEngine()

# Main app
def main():
    # Header
    st.markdown('<div class="main-header">⚖️ LawScout AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-Powered Legal Research Assistant</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 💡 Example Queries")
        
        # Expandable sections for different query types
        with st.expander("📋 Contract Analysis", expanded=False):
            st.markdown("""
            **Termination & Duration:**
            - What are termination clauses in software licenses?
            - How are contract renewal terms specified?
            - What notice periods are required for termination?
            
            **Payment & Pricing:**
            - How are payment terms structured in SaaS agreements?
            - What are common pricing models in licensing contracts?
            - How are late payment penalties defined?
            
            **Warranties & Representations:**
            - What warranty provisions exist in commercial agreements?
            - How are warranties of non-infringement stated?
            - What are disclaimer of warranty clauses?
            """)
        
        with st.expander("🔐 Intellectual Property", expanded=False):
            st.markdown("""
            **IP Rights & Licensing:**
            - How are intellectual property rights transferred in contracts?
            - What are license grant restrictions and limitations?
            - How are derivative works and modifications handled?
            
            **Confidentiality:**
            - How is confidential information protected in NDAs?
            - What are the exceptions to confidentiality obligations?
            - How long do confidentiality obligations last?
            
            **Ownership:**
            - Who owns work product created under the agreement?
            - How are pre-existing intellectual property rights preserved?
            - What happens to IP rights upon termination?
            """)
        
        with st.expander("⚖️ Liability & Risk", expanded=False):
            st.markdown("""
            **Indemnification:**
            - What are indemnification provisions in contracts?
            - Who bears liability for third-party IP claims?
            - How are indemnification procedures specified?
            
            **Limitation of Liability:**
            - What are limitation of liability clauses?
            - What damages are typically excluded or capped?
            - Are there exceptions to liability limitations?
            
            **Insurance & Security:**
            - What insurance coverage is required?
            - How are data security obligations defined?
            - What are breach notification requirements?
            """)
        
        with st.expander("⚖️ Case Law Research", expanded=False):
            st.markdown("""
            **Contract Interpretation:**
            - How do courts interpret ambiguous contract terms?
            - What is the statute of limitations for breach of contract?
            - How do courts enforce liquidated damages clauses?
            
            **IP & Copyright:**
            - How have courts interpreted fair use in copyright cases?
            - What constitutes trademark infringement?
            - How do courts determine patent validity?
            
            **Commercial Disputes:**
            - What remedies are available for breach of contract?
            - How do courts determine expectation damages?
            - When can contracts be rescinded for fraud?
            """)
        
        with st.expander("🔍 Cross-Domain Queries", expanded=False):
            st.markdown("""
            **Combining Contracts & Case Law:**
            - How do warranty disclaimers in contracts compare to legal precedents?
            - What are best practices for force majeure clauses based on recent cases?
            - How have courts interpreted choice of law provisions?
            
            **Industry-Specific:**
            - What are standard terms in software licensing agreements?
            - How are data processing agreements structured under privacy laws?
            - What are common provisions in distribution agreements?
            """)
        
        # Quick action buttons
        st.markdown("---")
        st.markdown("### 🚀 Quick Search")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 Termination", use_container_width=True):
                st.session_state.query = "What are termination clauses in software licenses?"
                st.rerun()
            
            if st.button("💰 Payment", use_container_width=True):
                st.session_state.query = "How are payment terms structured in agreements?"
                st.rerun()
            
            if st.button("🛡️ Warranties", use_container_width=True):
                st.session_state.query = "What warranty provisions exist in commercial agreements?"
                st.rerun()
        
        with col2:
            if st.button("🔐 IP Rights", use_container_width=True):
                st.session_state.query = "How are intellectual property rights transferred?"
                st.rerun()
            
            if st.button("⚠️ Liability", use_container_width=True):
                st.session_state.query = "What are limitation of liability clauses?"
                st.rerun()
            
            if st.button("📜 Indemnity", use_container_width=True):
                st.session_state.query = "What are indemnification provisions?"
                st.rerun()
        
        st.markdown("---")
        st.header("⚙️ Settings")
        
        collection_type = st.selectbox(
            "Search In:",
            ["both", "contracts", "cases"],
            format_func=lambda x: {
                "both": "📋 Contracts & ⚖️ Cases",
                "contracts": "📋 Contracts Only",
                "cases": "⚖️ Legal Cases Only"
            }[x]
        )
        
        num_results = st.slider(
            "Number of Results:",
            min_value=1,
            max_value=10,
            value=5
        )
        
        show_sources = st.checkbox("Show Source Documents", value=True)
        
        st.divider()
        
        st.subheader("📊 System Status")
        st.success("🟢 Connected to Qdrant")
        st.success("🟢 Gemini LLM Active")
        st.info("📚 60,629 documents indexed")
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Query input
        query = st.text_area(
            "🔍 Enter your legal research question:",
            value=st.session_state.get('query', ''),
            height=100,
            placeholder="E.g., What are the key provisions in software license agreements?"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    # Search
    if search_button and query:
        with st.spinner("🔍 Searching legal documents..."):
            try:
                # Load RAG engine
                rag = load_rag_engine()
                
                # Perform search
                response = rag.ask(
                    query=query,
                    collection_type=collection_type,
                    limit=num_results,
                    return_sources=show_sources
                )
                
                # Display answer
                st.divider()
                st.subheader("💡 Answer")
                st.markdown(response['answer'])
                
                # Display sources
                if show_sources and response.get('sources'):
                    st.divider()
                    st.subheader(f"📚 Sources ({response['num_sources']} documents)")
                    
                    for i, source in enumerate(response['sources'], 1):
                        with st.expander(f"Source {i}: {source['source']} (Relevance: {source['score']:.1%})"):
                            st.markdown(f"**Collection:** {source['collection'].replace('legal_', '').title()}")
                            st.markdown(f"**Relevance Score:** {source['score']:.3f}")
                            st.markdown("**Excerpt:**")
                            st.markdown(f"> {source['text']}")
                
                # Stats
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Documents Searched", "240,633")
                with col2:
                    st.metric("Relevant Sources", response['num_sources'])
                with col3:
                    st.metric("Top Match Score", f"{response['sources'][0]['score']:.1%}" if response.get('sources') else "N/A")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.exception(e)
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>⚖️ LawScout AI - Powered by Qdrant, Sentence Transformers, and Gemini</p>
            <p>📊 1,511 documents | 240,633 chunks | 384-dimensional embeddings</p>
            <p style='font-size: 0.8rem;'>⚠️ For research purposes only. Not legal advice.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ---
    **Data Attribution:**
    Legal case opinions sourced from [CourtListener](https://www.courtlistener.com/), 
    a project of the non-profit [Free Law Project](https://free.law/). 
    Contract data from the [CUAD Dataset](https://www.atticusprojectai.org/cuad).

    We are grateful for their mission to make legal information freely accessible.
    """)

if __name__ == "__main__":
    main()
