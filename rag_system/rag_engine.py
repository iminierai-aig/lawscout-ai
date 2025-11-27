"""
RAG (Retrieval Augmented Generation) Engine
Combines vector search with Gemini LLM for legal question answering
"""
import os
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LegalRAGEngine:
    """RAG engine for legal research"""
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        # Qdrant setup
        self.qdrant_url = qdrant_url or os.getenv('QDRANT_URL')
        self.qdrant_api_key = qdrant_api_key or os.getenv('QDRANT_API_KEY')
        
        print("🔌 Connecting to Qdrant...")
        self.qdrant_client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.qdrant_api_key
        )
        print("✅ Connected to Qdrant")
        
        # Embedding model setup
        print(f"📥 Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        print("✅ Embedding model loaded")
        
        # Gemini setup - Use gemini-pro instead of gemini-1.5-flash
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.llm = genai.GenerativeModel('gemini-2.5-flash')
            print("✅ Gemini LLM configured (gemini-2.5-flash)")
        else:
            self.llm = None
            print("⚠️  No Gemini API key - LLM disabled")
        
        self.collections = {
            'contracts': 'legal_contracts',
            'cases': 'legal_cases'
        }
    
    def search(
        self,
        query: str,
        collection_type: str = 'both',
        limit: int = 5
    ) -> List[Dict]:
        """
        Search vector database for relevant legal documents
        
        Args:
            query: Search query
            collection_type: 'contracts', 'cases', or 'both'
            limit: Number of results per collection
        
        Returns:
            List of relevant chunks with metadata
        """
        print(f"\n🔍 Searching: '{query}'")
        print(f"   Collection: {collection_type}")
        print(f"   Limit: {limit}")
        
        # Generate query embedding
        query_vector = self.encoder.encode(query).tolist()
        
        results = []
        
        # Determine which collections to search
        collections_to_search = []
        if collection_type == 'both':
            collections_to_search = list(self.collections.values())
        elif collection_type == 'contracts':
            collections_to_search = [self.collections['contracts']]
        elif collection_type == 'cases':
            collections_to_search = [self.collections['cases']]
        
        # Search each collection
        for collection_name in collections_to_search:
            try:
                search_result = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=limit
                )
                
                for hit in search_result:
                    results.append({
                        'collection': collection_name,
                        'score': hit.score,
                        'text': hit.payload.get('text', ''),
                        'chunk_id': hit.payload.get('chunk_id', ''),
                        'source': hit.payload.get('source', ''),
                        'metadata': {
                            k: v for k, v in hit.payload.items() 
                            if k not in ['text', 'chunk_id', 'source', 'sentences', 'embedding']
                        }
                    })
                
                print(f"   ✓ Found {len(search_result)} results in {collection_name}")
                
            except Exception as e:
                print(f"   ⚠️  Error searching {collection_name}: {e}")
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"✅ Total results: {len(results)}")
        return results
    
    def generate_answer(
        self,
        query: str,
        context: List[Dict],
        max_context_length: int = 3000
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User's question
            context: Retrieved chunks from vector search
            max_context_length: Maximum characters for context
        
        Returns:
            Generated answer
        """
        if not self.llm:
            return "❌ Gemini API not configured. Set GEMINI_API_KEY in .env"
        
        # Build context from top results
        context_text = ""
        for i, chunk in enumerate(context[:5]):  # Top 5 chunks
            text = chunk['text'][:500]  # First 500 chars of each
            source = chunk.get('metadata', {}).get('case_name') or \
                     chunk.get('metadata', {}).get('filename', 'Unknown')
            
            context_text += f"\n[Source {i+1}: {source}]\n{text}\n"
            
            if len(context_text) > max_context_length:
                break
        
        # Create prompt
        prompt = f"""You are a legal research assistant. Answer the question based on the provided legal documents.

Question: {query}

Relevant Legal Documents:
{context_text}

Instructions:
1. Answer based ONLY on the provided documents
2. Cite sources by number [Source 1], [Source 2], etc.
3. If the documents don't contain enough information, say so
4. Be precise and use legal terminology where appropriate
5. Keep answer concise but complete

Answer:"""
        
        try:
            print("\n🤖 Generating answer with Gemini...")
            response = self.llm.generate_content(prompt)
            answer = response.text
            print("✅ Answer generated")
            return answer
        
        except Exception as e:
            print(f"⚠️  Gemini error: {e}")
            return f"❌ Error generating answer: {e}"
    
    def ask(
        self,
        query: str,
        collection_type: str = 'both',
        limit: int = 5,
        return_sources: bool = True
    ) -> Dict:
        """
        Complete RAG pipeline: search + generate
        
        Args:
            query: User's question
            collection_type: Which collections to search
            limit: Number of chunks to retrieve
            return_sources: Include source documents in response
        
        Returns:
            Dict with answer and optional sources
        """
        print("\n" + "=" * 60)
        print("💬 Legal Research Query")
        print("=" * 60)
        
        # Step 1: Vector search
        results = self.search(query, collection_type, limit)
        
        if not results:
            return {
                'answer': 'No relevant documents found for your query.',
                'sources': []
            }
        
        # Step 2: Generate answer
        answer = self.generate_answer(query, results)
        
        # Step 3: Prepare response
        response = {
            'answer': answer,
            'num_sources': len(results)
        }
        
        if return_sources:
            response['sources'] = [
                {
                    'score': r['score'],
                    'text': r['text'][:200] + '...',
                    'source': r.get('metadata', {}).get('case_name') or \
                              r.get('metadata', {}).get('filename', 'Unknown'),
                    'collection': r['collection']
                }
                for r in results[:5]
            ]
        
        return response

def demo():
    """Demo the RAG engine"""
    
    print("\n" + "=" * 60)
    print("🎯 LawScout AI - RAG Engine Demo")
    print("=" * 60)
    
    # Initialize engine
    rag = LegalRAGEngine()
    
    # Example queries
    queries = [
        "What are the termination clauses in software license agreements?",
        "What is the doctrine of sovereign immunity?",
        "How are intellectual property rights transferred in contracts?"
    ]
    
    for query in queries:
        response = rag.ask(query, collection_type='both', limit=5)
        
        print("\n" + "=" * 60)
        print(f"❓ Query: {query}")
        print("=" * 60)
        print(f"\n💡 Answer:\n{response['answer']}")
        print(f"\n📚 Sources: {response['num_sources']} documents")
        
        if response.get('sources'):
            print("\n📖 Top Sources:")
            for i, source in enumerate(response['sources'][:3], 1):
                print(f"\n{i}. {source['source']} (score: {source['score']:.3f})")
                print(f"   {source['text']}")
        
        print("\n" + "-" * 60)
        input("Press Enter for next query...")

if __name__ == "__main__":
    demo()
