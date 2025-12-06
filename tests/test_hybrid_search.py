"""
Tests for Hybrid Search and Reranking
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.hybrid_search import HybridSearchEngine


class TestHybridSearch(unittest.TestCase):
    """Test cases for hybrid search functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_documents = [
            {
                'chunk_id': '1',
                'text': 'Contract termination requires thirty days written notice to the other party',
                'score': 0.95
            },
            {
                'chunk_id': '2',
                'text': 'Software license agreement with payment terms and conditions',
                'score': 0.85
            },
            {
                'chunk_id': '3',
                'text': 'Indemnification provisions protect parties from legal liability',
                'score': 0.75
            },
            {
                'chunk_id': '4',
                'text': 'Termination clause allows ending the contract under specific conditions',
                'score': 0.70
            }
        ]
    
    @patch('rag_system.hybrid_search.CrossEncoder')
    def test_initialization_with_reranking(self, mock_cross_encoder):
        """Test hybrid search engine initializes correctly with reranking"""
        mock_cross_encoder.return_value = Mock()
        
        engine = HybridSearchEngine(use_reranking=True)
        
        self.assertIsNotNone(engine)
        self.assertTrue(engine.use_reranking)
        mock_cross_encoder.assert_called_once()
    
    def test_initialization_without_reranking(self):
        """Test hybrid search engine initializes correctly without reranking"""
        engine = HybridSearchEngine(use_reranking=False)
        
        self.assertIsNotNone(engine)
        self.assertFalse(engine.use_reranking)
        self.assertIsNone(engine.reranker)
    
    def test_create_bm25_index(self):
        """Test BM25 index creation"""
        engine = HybridSearchEngine(use_reranking=False)
        
        documents = [doc['text'] for doc in self.sample_documents]
        bm25_index = engine.create_bm25_index(documents)
        
        self.assertIsNotNone(bm25_index)
    
    def test_bm25_search(self):
        """Test BM25 keyword search"""
        engine = HybridSearchEngine(use_reranking=False)
        
        query = "termination contract"
        results = engine.bm25_search(
            query=query,
            documents=self.sample_documents,
            top_k=2
        )
        
        self.assertEqual(len(results), 2)
        self.assertIn('bm25_score', results[0])
        # Document 1 and 4 should rank higher (both mention termination)
        self.assertIn('termination', results[0]['text'].lower())
    
    def test_hybrid_search(self):
        """Test hybrid search combining semantic and BM25"""
        engine = HybridSearchEngine(use_reranking=False)
        
        query = "termination notice"
        results = engine.hybrid_search(
            query=query,
            semantic_results=self.sample_documents,
            alpha=0.5,  # Equal weight
            top_k=3
        )
        
        self.assertLessEqual(len(results), 3)
        self.assertIn('hybrid_score', results[0])
        self.assertIn('semantic_score', results[0])
        self.assertIn('bm25_score', results[0])
    
    @patch('rag_system.hybrid_search.CrossEncoder')
    def test_reranking(self, mock_cross_encoder):
        """Test cross-encoder reranking"""
        # Setup mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = np.array([0.9, 0.7, 0.8, 0.6])
        mock_cross_encoder.return_value = mock_reranker
        
        engine = HybridSearchEngine(use_reranking=True)
        
        query = "termination clause"
        reranked = engine.rerank(
            query=query,
            documents=self.sample_documents,
            top_k=2
        )
        
        self.assertEqual(len(reranked), 2)
        self.assertIn('rerank_score', reranked[0])
        # Should be sorted by rerank score
        self.assertGreater(reranked[0]['rerank_score'], reranked[1]['rerank_score'])
    
    @patch('rag_system.hybrid_search.CrossEncoder')
    def test_search_with_reranking_pipeline(self, mock_cross_encoder):
        """Test complete hybrid search with reranking pipeline"""
        # Setup mock reranker
        mock_reranker = Mock()
        mock_reranker.predict.return_value = np.array([0.9, 0.8, 0.7, 0.6])
        mock_cross_encoder.return_value = mock_reranker
        
        engine = HybridSearchEngine(use_reranking=True)
        
        query = "contract termination"
        results = engine.search_with_reranking(
            query=query,
            semantic_results=self.sample_documents,
            alpha=0.7,  # 70% semantic, 30% BM25
            top_k=2,
            rerank_top_k=3
        )
        
        self.assertLessEqual(len(results), 2)
        self.assertIn('rerank_score', results[0])
    
    def test_empty_documents(self):
        """Test handling of empty document list"""
        engine = HybridSearchEngine(use_reranking=False)
        
        results = engine.bm25_search(
            query="test",
            documents=[],
            top_k=5
        )
        
        self.assertEqual(len(results), 0)
    
    def test_hybrid_search_alpha_weights(self):
        """Test that alpha parameter correctly weights scores"""
        engine = HybridSearchEngine(use_reranking=False)
        
        query = "test query"
        
        # Test with alpha=1 (pure semantic)
        results_semantic = engine.hybrid_search(
            query=query,
            semantic_results=self.sample_documents,
            alpha=1.0,
            top_k=2
        )
        
        # Test with alpha=0 (pure BM25)
        results_bm25 = engine.hybrid_search(
            query=query,
            semantic_results=self.sample_documents,
            alpha=0.0,
            top_k=2
        )
        
        # Both should return results
        self.assertGreater(len(results_semantic), 0)
        self.assertGreater(len(results_bm25), 0)


class TestHybridSearchIntegration(unittest.TestCase):
    """Integration tests for hybrid search"""
    
    def test_end_to_end_search(self):
        """Test complete search pipeline"""
        # This would test with real models if available
        # For now, placeholder
        pass


if __name__ == '__main__':
    unittest.main()

