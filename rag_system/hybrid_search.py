"""
Hybrid Search Engine
Combines semantic search (embeddings) with keyword search (BM25)
Includes cross-encoder reranking for improved relevance
"""
from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np


class HybridSearchEngine:
    """
    Hybrid search combining semantic and keyword search with reranking
    """
    
    def __init__(
        self,
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        use_reranking: bool = True
    ):
        """
        Initialize hybrid search engine
        
        Args:
            reranker_model: Cross-encoder model for reranking
            use_reranking: Whether to use cross-encoder reranking
        """
        self.use_reranking = use_reranking
        
        if use_reranking:
            print(f"📥 Loading reranker: {reranker_model}")
            self.reranker = CrossEncoder(reranker_model)
            print("✅ Reranker loaded")
        else:
            self.reranker = None
    
    def create_bm25_index(self, documents: List[str]) -> BM25Okapi:
        """
        Create BM25 index from documents
        
        Args:
            documents: List of document texts
        
        Returns:
            BM25 index
        """
        # Tokenize documents
        tokenized_docs = [doc.lower().split() for doc in documents]
        
        # Create BM25 index
        bm25 = BM25Okapi(tokenized_docs)
        
        return bm25
    
    def bm25_search(
        self,
        query: str,
        documents: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Perform BM25 keyword search
        
        Args:
            query: Search query
            documents: List of document dictionaries with 'text' field
            top_k: Number of results to return
        
        Returns:
            Top-k documents with BM25 scores
        """
        # Extract text from documents
        texts = [doc.get('text', '') for doc in documents]
        
        # Create BM25 index
        bm25 = self.create_bm25_index(texts)
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # Create results
        results = []
        for idx in top_indices:
            doc = documents[idx].copy()
            doc['bm25_score'] = float(scores[idx])
            results.append(doc)
        
        return results
    
    def hybrid_search(
        self,
        query: str,
        semantic_results: List[Dict],
        all_documents: Optional[List[Dict]] = None,
        alpha: float = 0.5,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Combine semantic and BM25 search results
        
        Args:
            query: Search query
            semantic_results: Results from semantic search (with 'score' field)
            all_documents: Full document corpus for BM25 (optional)
            alpha: Weight for semantic scores (1-alpha for BM25)
            top_k: Number of final results
        
        Returns:
            Hybrid-ranked results
        """
        # If no additional documents provided, use semantic results for BM25
        if all_documents is None:
            all_documents = semantic_results
        
        # Perform BM25 search
        bm25_results = self.bm25_search(query, all_documents, top_k=top_k*2)
        
        # Create lookup dictionaries
        semantic_scores = {
            doc.get('chunk_id', i): doc.get('score', 0)
            for i, doc in enumerate(semantic_results)
        }
        
        bm25_scores = {
            doc.get('chunk_id', i): doc.get('bm25_score', 0)
            for i, doc in enumerate(bm25_results)
        }
        
        # Normalize scores to [0, 1]
        max_semantic = max(semantic_scores.values()) if semantic_scores else 1
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1
        
        # Combine all documents
        all_doc_ids = set(semantic_scores.keys()) | set(bm25_scores.keys())
        
        # Calculate hybrid scores
        hybrid_results = []
        seen_ids = set()
        
        for doc_id in all_doc_ids:
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            
            # Get document (prefer from semantic results)
            doc = None
            for d in semantic_results:
                if d.get('chunk_id', None) == doc_id:
                    doc = d.copy()
                    break
            
            if doc is None:
                for d in bm25_results:
                    if d.get('chunk_id', None) == doc_id:
                        doc = d.copy()
                        break
            
            if doc is None:
                continue
            
            # Normalize scores
            sem_score = semantic_scores.get(doc_id, 0) / max_semantic
            bm25_score = bm25_scores.get(doc_id, 0) / max_bm25
            
            # Calculate hybrid score
            hybrid_score = alpha * sem_score + (1 - alpha) * bm25_score
            
            doc['semantic_score'] = float(semantic_scores.get(doc_id, 0))
            doc['bm25_score'] = float(bm25_scores.get(doc_id, 0))
            doc['hybrid_score'] = float(hybrid_score)
            doc['score'] = float(hybrid_score)  # Update main score
            
            hybrid_results.append(doc)
        
        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        return hybrid_results[:top_k]
    
    def rerank(
        self,
        query: str,
        documents: List[Dict],
        top_k: Optional[int] = None
    ) -> List[Dict]:
        """
        Rerank documents using cross-encoder
        
        Args:
            query: Search query
            documents: Documents to rerank
            top_k: Number of results to return (None = all)
        
        Returns:
            Reranked documents with rerank_score
        """
        if not self.use_reranking or not self.reranker:
            return documents
        
        if not documents:
            return documents
        
        # Prepare query-document pairs
        pairs = [
            [query, doc.get('text', '')[:512]]  # Limit to 512 chars for efficiency
            for doc in documents
        ]
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Add rerank scores to documents
        reranked_docs = []
        for doc, score in zip(documents, rerank_scores):
            doc_copy = doc.copy()
            doc_copy['rerank_score'] = float(score)
            doc_copy['score'] = float(score)  # Update main score
            reranked_docs.append(doc_copy)
        
        # Sort by rerank score
        reranked_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        if top_k:
            return reranked_docs[:top_k]
        
        return reranked_docs
    
    def search_with_reranking(
        self,
        query: str,
        semantic_results: List[Dict],
        all_documents: Optional[List[Dict]] = None,
        alpha: float = 0.5,
        top_k: int = 10,
        rerank_top_k: int = 50
    ) -> List[Dict]:
        """
        Complete hybrid search with reranking pipeline
        
        Args:
            query: Search query
            semantic_results: Semantic search results
            all_documents: Full corpus for BM25 (optional)
            alpha: Semantic weight
            top_k: Final number of results
            rerank_top_k: Number of results before reranking
        
        Returns:
            Final reranked results
        """
        # Step 1: Hybrid search
        hybrid_results = self.hybrid_search(
            query=query,
            semantic_results=semantic_results,
            all_documents=all_documents,
            alpha=alpha,
            top_k=rerank_top_k
        )
        
        # Step 2: Rerank top results
        final_results = self.rerank(
            query=query,
            documents=hybrid_results,
            top_k=top_k
        )
        
        return final_results


def test_hybrid_search():
    """Test hybrid search functionality"""
    
    # Sample documents
    documents = [
        {
            'chunk_id': '1',
            'text': 'Contract termination clause requires 30 days notice',
            'score': 0.95
        },
        {
            'chunk_id': '2',
            'text': 'Software license agreement with payment terms',
            'score': 0.85
        },
        {
            'chunk_id': '3',
            'text': 'Indemnification provisions in commercial contracts',
            'score': 0.75
        }
    ]
    
    # Initialize hybrid search
    hybrid_search = HybridSearchEngine(use_reranking=True)
    
    # Test query
    query = "termination clause"
    
    # Hybrid search
    results = hybrid_search.search_with_reranking(
        query=query,
        semantic_results=documents,
        top_k=3
    )
    
    print(f"Query: {query}")
    print(f"\nResults:")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc['text'][:50]}...")
        print(f"   Rerank Score: {doc.get('rerank_score', 0):.3f}")
        print(f"   Hybrid Score: {doc.get('hybrid_score', 0):.3f}")
        print()


if __name__ == "__main__":
    test_hybrid_search()

