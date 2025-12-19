"""
RAG (Retrieval Augmented Generation) Engine
Combines vector search with Gemini LLM for legal question answering
Features: Hybrid search, reranking, advanced filtering, citation extraction
"""
import os
from typing import List, Dict, Optional, Generator
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime
import json

from .hybrid_search import HybridSearchEngine
from .citation_utils import CitationExtractor

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
        
        # Gemini setup - Use gemini-2.5-flash (latest and best!)
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            try:
                # Use Gemini 2.5 Flash - the newest model
                self.llm = genai.GenerativeModel('gemini-2.5-flash')
                print("✅ Gemini LLM configured (gemini-2.5-flash - Latest!)")
            except Exception as e:
                self.llm = None
                print(f"⚠️  Gemini configuration error: {e}")
        else:
            self.llm = None
            print("⚠️  No Gemini API key - LLM disabled")
        
        self.collections = {
            'contracts': 'legal_contracts',
            'cases': 'legal_cases'
        }
        
        # Analytics tracking
        self.analytics = []
        
        # Hybrid search and reranking
        print("📥 Initializing hybrid search engine...")
        self.hybrid_search = HybridSearchEngine(use_reranking=True)
        print("✅ Hybrid search engine ready")
        
        # Citation extraction
        self.citation_extractor = CitationExtractor()
    
    def search(
        self,
        query: str,
        collection_type: str = 'both',
        limit: int = 5,
        filters: Optional[Dict] = None,
        use_hybrid: bool = True,
        use_reranking: bool = True
    ) -> List[Dict]:
        """
        Search vector database for relevant legal documents
        
        Args:
            query: Search query
            collection_type: 'contracts', 'cases', or 'both'
            limit: Number of results per collection
            filters: Optional filters (date_range, jurisdiction, court)
            use_hybrid: Use hybrid search (semantic + BM25)
            use_reranking: Use cross-encoder reranking
        
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
        
        # Build Qdrant filters if provided
        qdrant_filter = self._build_qdrant_filter(filters) if filters else None
        
        # Search each collection
        for collection_name in collections_to_search:
            try:
                # Increase initial limit for hybrid/reranking
                initial_limit = limit * 3 if (use_hybrid or use_reranking) else limit
                
                search_result = self.qdrant_client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    limit=initial_limit,
                    query_filter=qdrant_filter
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
        
        # Apply hybrid search and reranking if enabled
        if results and (use_hybrid or use_reranking):
            if use_hybrid:
                print("   🔄 Applying hybrid search (semantic + BM25)...")
                results = self.hybrid_search.hybrid_search(
                    query=query,
                    semantic_results=results,
                    alpha=0.7,  # 70% semantic, 30% BM25
                    top_k=limit * 2
                )
            
            if use_reranking:
                print("   🎯 Reranking results with cross-encoder...")
                results = self.hybrid_search.rerank(
                    query=query,
                    documents=results,
                    top_k=limit
                )
        else:
            # Sort by score
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:limit]
        
        print(f"✅ Total results: {len(results)}")
        return results
    
    def _build_qdrant_filter(self, filters: Dict) -> Optional[Filter]:
        """
        Build Qdrant filter from filter dictionary
        
        Args:
            filters: Dict with 'date_range', 'jurisdiction', 'court', etc.
        
        Returns:
            Qdrant Filter object or None if filters not supported
        
        Note: Filters require indexed fields in Qdrant. If your data doesn't
              have these fields indexed, filters will be skipped silently.
        """
        # For now, return None to skip filtering until metadata is indexed
        # Users can enable this once their Qdrant collections have the required fields
        print("   ℹ️  Advanced filters skipped (requires indexed metadata fields)")
        return None
        
        # UNCOMMENT BELOW when your Qdrant data has these indexed fields:
        # conditions = []
        # 
        # # Date range filter
        # if 'date_range' in filters and filters['date_range']:
        #     start_date, end_date = filters['date_range']
        #     if start_date:
        #         conditions.append(
        #             FieldCondition(
        #                 key="date_filed",
        #                 range=Range(gte=start_date, lte=end_date or "9999-12-31")
        #             )
        #         )
        # 
        # # Jurisdiction filter
        # if 'jurisdiction' in filters and filters['jurisdiction']:
        #     conditions.append(
        #         FieldCondition(
        #             key="jurisdiction",
        #             match=MatchValue(value=filters['jurisdiction'])
        #         )
        #     )
        # 
        # # Court filter
        # if 'court' in filters and filters['court']:
        #     conditions.append(
        #         FieldCondition(
        #             key="court",
        #             match=MatchValue(value=filters['court'])
        #         )
        #     )
        # 
        # if conditions:
        #     return Filter(must=conditions)
        # 
        # return None
    
    def generate_answer(
        self,
        query: str,
        context: List[Dict],
        max_context_length: int = 3000,
        stream: bool = False
    ) -> str | Generator[str, None, None]:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: User's question
            context: Retrieved chunks from vector search
            max_context_length: Maximum characters for context
            stream: Whether to stream the response
        
        Returns:
            Generated answer (string or generator if streaming)
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
            
            if stream:
                # Return generator for streaming
                response = self.llm.generate_content(prompt, stream=True)
                return (chunk.text for chunk in response)
            else:
                # Return complete answer
                response = self.llm.generate_content(prompt)
                answer = response.text
                print("✅ Answer generated")
                return answer
        
        except Exception as e:
            print(f"⚠️  Gemini error: {e}")
            # Return a helpful message with the context anyway
            fallback = f"""⚠️ LLM Answer Generation Unavailable

The search found {len(context)} highly relevant documents ranked by our advanced hybrid search + reranking system.

**Please review the source documents below** - they contain the information you need!

💡 Tip: The search results are ranked by relevance using:
   • Semantic understanding (meaning-based)
   • Keyword matching (BM25)
   • Cross-encoder reranking (ML-powered relevance)

Note: LLM answer generation is temporarily unavailable. Check your Gemini API key or quota."""
            return fallback
    
    def ask(
        self,
        query: str,
        collection_type: str = 'both',
        limit: int = 5,
        return_sources: bool = True,
        stream: bool = False,
        filters: Optional[Dict] = None,
        use_hybrid: bool = True,
        use_reranking: bool = True,
        extract_citations: bool = True
    ) -> Dict:
        """
        Complete RAG pipeline: search + generate with advanced features
        
        Args:
            query: User's question
            collection_type: Which collections to search
            limit: Number of chunks to retrieve
            return_sources: Include source documents in response
            stream: Whether to stream the LLM response
            filters: Advanced filters (date, jurisdiction, court)
            use_hybrid: Use hybrid search (semantic + BM25)
            use_reranking: Use cross-encoder reranking
            extract_citations: Extract and link citations
        
        Returns:
            Dict with answer, sources, and metadata
        """
        start_time = datetime.now()
        
        print("\n" + "=" * 60)
        print("💬 Legal Research Query")
        print("=" * 60)
        
        # Step 1: Advanced search with hybrid + reranking
        search_start = datetime.now()
        results = self.search(
            query=query,
            collection_type=collection_type,
            limit=limit,
            filters=filters,
            use_hybrid=use_hybrid,
            use_reranking=use_reranking
        )
        search_time = (datetime.now() - search_start).total_seconds()
        
        if not results:
            self._track_analytics(query, collection_type, 0, 0, search_time, 0)
            return {
                'answer': 'No relevant documents found for your query.',
                'sources': []
            }
        
        # Step 2: Generate answer
        gen_start = datetime.now()
        answer = self.generate_answer(query, results, stream=stream)
        
        # If streaming, don't calculate gen_time yet
        gen_time = 0 if stream else (datetime.now() - gen_start).total_seconds()
        
        # Step 3: Prepare response
        response = {
            'answer': answer,
            'num_sources': len(results),
            'search_time': search_time,
            'generation_time': gen_time
        }
        
        if return_sources:
            response['sources'] = []
            for r in results[:5]:
                # Preserve original metadata from search results
                original_metadata = r.get('metadata', {})
                
                source_dict = {
                    'score': r['score'],
                    'text': r['text'][:200] + '...',
                    'full_text': r['text'],  # Include full text
                    'source': original_metadata.get('case_name') or \
                              original_metadata.get('filename') or \
                              r.get('source', 'Unknown'),
                    'collection': r.get('collection', 'unknown'),
                    'metadata': original_metadata  # Preserve full metadata
                }
                
                # Add search method scores if available
                if 'semantic_score' in r:
                    source_dict['semantic_score'] = r['semantic_score']
                if 'bm25_score' in r:
                    source_dict['bm25_score'] = r['bm25_score']
                if 'rerank_score' in r:
                    source_dict['rerank_score'] = r['rerank_score']
                
                # Extract citations if enabled
                if extract_citations:
                    citations = self.citation_extractor.extract_citations(r['text'])
                    if citations:
                        source_dict['citations'] = citations[:3]  # Top 3 citations
                
                response['sources'].append(source_dict)
        
        # Track analytics (only if not streaming)
        if not stream:
            total_time = (datetime.now() - start_time).total_seconds()
            self._track_analytics(
                query, 
                collection_type, 
                len(results), 
                results[0]['score'] if results else 0,
                search_time,
                gen_time
            )
        
        return response
    
    def _track_analytics(self, query: str, collection: str, num_results: int, 
                        top_score: float, search_time: float, gen_time: float):
        """Track query analytics"""
        self.analytics.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'collection': collection,
            'num_results': num_results,
            'top_score': top_score,
            'search_time': search_time,
            'generation_time': gen_time,
            'total_time': search_time + gen_time
        })
        
        # Keep only last 1000 queries in memory
        if len(self.analytics) > 1000:
            self.analytics = self.analytics[-1000:]
    
    def get_analytics(self) -> List[Dict]:
        """Get analytics data"""
        return self.analytics
    
    def save_analytics(self, filepath: str = 'analytics.json'):
        """Save analytics to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.analytics, f, indent=2)
            print(f"✅ Analytics saved to {filepath}")
        except Exception as e:
            print(f"⚠️  Error saving analytics: {e}")

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