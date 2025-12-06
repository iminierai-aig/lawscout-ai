"""
Unit tests for RAG Engine
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.rag_engine import LegalRAGEngine


class TestLegalRAGEngine(unittest.TestCase):
    """Test cases for LegalRAGEngine"""
    
    @patch('rag_system.rag_engine.QdrantClient')
    @patch('rag_system.rag_engine.SentenceTransformer')
    @patch('rag_system.rag_engine.genai')
    def setUp(self, mock_genai, mock_transformer, mock_qdrant):
        """Set up test fixtures"""
        # Mock dependencies
        self.mock_qdrant = mock_qdrant.return_value
        self.mock_encoder = mock_transformer.return_value
        self.mock_llm = Mock()
        mock_genai.GenerativeModel.return_value = self.mock_llm
        
        # Create engine with mocked dependencies
        self.engine = LegalRAGEngine(
            qdrant_url="http://test",
            qdrant_api_key="test_key",
            gemini_api_key="test_gemini_key"
        )
    
    def test_initialization(self):
        """Test engine initializes correctly"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.collections['contracts'], 'legal_contracts')
        self.assertEqual(self.engine.collections['cases'], 'legal_cases')
        self.assertIsInstance(self.engine.analytics, list)
    
    @patch('rag_system.rag_engine.QdrantClient')
    @patch('rag_system.rag_engine.SentenceTransformer')
    def test_search_contracts_only(self, mock_transformer, mock_qdrant):
        """Test searching contracts collection only"""
        # Setup mocks
        mock_client = mock_qdrant.return_value
        mock_encoder = mock_transformer.return_value
        mock_encoder.encode.return_value.tolist.return_value = [0.1] * 384
        
        # Mock search results
        mock_hit = Mock()
        mock_hit.score = 0.95
        mock_hit.payload = {
            'text': 'Test contract text',
            'chunk_id': 'chunk_1',
            'source': 'test_contract.pdf',
            'filename': 'test_contract.pdf'
        }
        mock_client.search.return_value = [mock_hit]
        
        # Create engine
        engine = LegalRAGEngine(
            qdrant_url="http://test",
            qdrant_api_key="test_key",
            gemini_api_key="test_key"
        )
        
        # Test search
        results = engine.search("test query", collection_type='contracts', limit=5)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['score'], 0.95)
        self.assertEqual(results[0]['text'], 'Test contract text')
        self.assertEqual(results[0]['collection'], 'legal_contracts')
    
    def test_track_analytics(self):
        """Test analytics tracking"""
        self.engine._track_analytics(
            query="test query",
            collection="both",
            num_results=5,
            top_score=0.95,
            search_time=0.5,
            gen_time=1.2
        )
        
        self.assertEqual(len(self.engine.analytics), 1)
        analytics = self.engine.analytics[0]
        
        self.assertEqual(analytics['query'], "test query")
        self.assertEqual(analytics['collection'], "both")
        self.assertEqual(analytics['num_results'], 5)
        self.assertEqual(analytics['top_score'], 0.95)
        self.assertEqual(analytics['search_time'], 0.5)
        self.assertEqual(analytics['generation_time'], 1.2)
        self.assertEqual(analytics['total_time'], 1.7)
    
    def test_analytics_limit(self):
        """Test analytics list is limited to 1000 entries"""
        # Add 1100 queries
        for i in range(1100):
            self.engine._track_analytics(
                query=f"query_{i}",
                collection="both",
                num_results=5,
                top_score=0.9,
                search_time=0.5,
                gen_time=1.0
            )
        
        # Should only keep last 1000
        self.assertEqual(len(self.engine.analytics), 1000)
        # First entry should be query_100
        self.assertEqual(self.engine.analytics[0]['query'], 'query_100')
    
    def test_get_analytics(self):
        """Test getting analytics data"""
        self.engine._track_analytics(
            query="test",
            collection="both",
            num_results=5,
            top_score=0.9,
            search_time=0.5,
            gen_time=1.0
        )
        
        analytics = self.engine.get_analytics()
        self.assertIsInstance(analytics, list)
        self.assertEqual(len(analytics), 1)
    
    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_analytics(self, mock_json_dump, mock_open):
        """Test saving analytics to file"""
        self.engine._track_analytics(
            query="test",
            collection="both",
            num_results=5,
            top_score=0.9,
            search_time=0.5,
            gen_time=1.0
        )
        
        self.engine.save_analytics('test_analytics.json')
        
        mock_open.assert_called_once_with('test_analytics.json', 'w')
        mock_json_dump.assert_called_once()


class TestQueryProcessing(unittest.TestCase):
    """Test query processing functionality"""
    
    def test_query_sanitization(self):
        """Test that queries are properly sanitized"""
        # This would test input validation
        # For now, placeholder
        pass
    
    def test_empty_query_handling(self):
        """Test handling of empty queries"""
        # Placeholder for empty query test
        pass


if __name__ == '__main__':
    unittest.main()

