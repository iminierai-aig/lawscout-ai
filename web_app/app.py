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
        
        st.divider()
        
        st.subheader("💡 Example Queries")
        examples = [
            "What are termination clauses?",
            "How is IP transferred?",
            "Sovereign immunity doctrine",
            "Non-compete agreements",
            "Force majeure provisions"
        ]
        
        for example in examples:
            if st.button(example, key=example):
                st.session_state.query = example
    
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

if __name__ == "__main__":
    main()

# Add to footer section (find st.markdown in footer)

st.markdown("""
---
**Data Attribution:**
Legal case opinions sourced from [CourtListener](https://www.courtlistener.com/), 
a project of the non-profit [Free Law Project](https://free.law/). 
Contract data from the [CUAD Dataset](https://www.atticusprojectai.org/cuad).

We are grateful for their mission to make legal information freely accessible.
""")
