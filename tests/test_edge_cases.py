"""
Edge Case Tests for Bug Fixes
Tests for division by zero and generator exception handling
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag_system.hybrid_search import HybridSearchEngine


class TestDivisionByZeroFix(unittest.TestCase):
    """Test cases for Bug 1: Division by zero in hybrid search"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = HybridSearchEngine(use_reranking=False)
    
    def test_all_zero_semantic_scores(self):
        """Test that all zero semantic scores don't cause division by zero"""
        documents = [
            {'chunk_id': '1', 'text': 'document one', 'score': 0.0},
            {'chunk_id': '2', 'text': 'document two', 'score': 0.0},
        ]
        
        # This should not raise ZeroDivisionError
        try:
            results = self.engine.hybrid_search(
                query="test query",
                semantic_results=documents,
                alpha=0.5,
                top_k=2
            )
            # Should return results without error
            self.assertIsInstance(results, list)
        except ZeroDivisionError:
            self.fail("Division by zero occurred with all-zero semantic scores")
    
    def test_all_zero_bm25_scores(self):
        """Test that all zero BM25 scores don't cause division by zero"""
        # Documents with very low BM25 scores (could round to 0)
        documents = [
            {'chunk_id': '1', 'text': 'a', 'score': 0.9},
            {'chunk_id': '2', 'text': 'b', 'score': 0.8},
        ]
        
        # Query that doesn't match any keywords
        try:
            results = self.engine.hybrid_search(
                query="zzzzzzzzz",  # No matches
                semantic_results=documents,
                alpha=0.5,
                top_k=2
            )
            self.assertIsInstance(results, list)
        except ZeroDivisionError:
            self.fail("Division by zero occurred with all-zero BM25 scores")
    
    def test_mixed_zero_and_nonzero_scores(self):
        """Test mixed zero and non-zero scores"""
        documents = [
            {'chunk_id': '1', 'text': 'document one', 'score': 0.0},
            {'chunk_id': '2', 'text': 'document two', 'score': 0.5},
            {'chunk_id': '3', 'text': 'document three', 'score': 0.0},
        ]
        
        try:
            results = self.engine.hybrid_search(
                query="test",
                semantic_results=documents,
                alpha=0.7,
                top_k=3
            )
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
        except ZeroDivisionError:
            self.fail("Division by zero with mixed scores")
    
    def test_empty_semantic_scores(self):
        """Test empty semantic scores dictionary"""
        documents = []
        
        try:
            results = self.engine.hybrid_search(
                query="test",
                semantic_results=documents,
                alpha=0.5,
                top_k=5
            )
            self.assertEqual(len(results), 0)
        except ZeroDivisionError:
            self.fail("Division by zero with empty semantic scores")


class TestGeneratorExceptionHandling(unittest.TestCase):
    """Test cases for Bug 2: Generator exception handling"""
    
    @patch('rag_system.rag_engine.QdrantClient')
    @patch('rag_system.rag_engine.SentenceTransformer')
    @patch('rag_system.rag_engine.genai')
    def test_streaming_generator_catches_exceptions(self, mock_genai, mock_transformer, mock_qdrant):
        """Test that streaming generator catches exceptions during iteration"""
        from rag_system.rag_engine import LegalRAGEngine
        
        # Setup mocks
        mock_llm = Mock()
        mock_genai.GenerativeModel.return_value = mock_llm
        
        # Create mock streaming response that raises exception
        class FailingChunk:
            @property
            def text(self):
                raise Exception("API Error during streaming")
        
        mock_response = [FailingChunk()]
        mock_llm.generate_content.return_value = mock_response
        
        # Create engine
        engine = LegalRAGEngine(
            qdrant_url="http://test",
            qdrant_api_key="test",
            gemini_api_key="test"
        )
        
        # Generate with streaming
        context = [{'text': 'test context', 'metadata': {}}]
        generator = engine.generate_answer("test query", context, stream=True)
        
        # Consuming generator should not raise exception, should handle it gracefully
        result_chunks = []
        try:
            for chunk in generator:
                result_chunks.append(chunk)
            # Should get error message as chunk
            self.assertTrue(any('interrupted' in str(chunk) or 'Error' in str(chunk) 
                              for chunk in result_chunks))
        except Exception as e:
            self.fail(f"Generator should catch exceptions, but raised: {e}")
    
    @patch('rag_system.rag_engine.QdrantClient')
    @patch('rag_system.rag_engine.SentenceTransformer')
    @patch('rag_system.rag_engine.genai')
    def test_successful_streaming(self, mock_genai, mock_transformer, mock_qdrant):
        """Test that successful streaming works correctly"""
        from rag_system.rag_engine import LegalRAGEngine
        
        # Setup mocks
        mock_llm = Mock()
        mock_genai.GenerativeModel.return_value = mock_llm
        
        # Create mock successful streaming response
        class SuccessChunk:
            def __init__(self, text):
                self._text = text
            
            @property
            def text(self):
                return self._text
        
        mock_response = [
            SuccessChunk("Hello "),
            SuccessChunk("world "),
            SuccessChunk("from "),
            SuccessChunk("Gemini")
        ]
        mock_llm.generate_content.return_value = mock_response
        
        # Create engine
        engine = LegalRAGEngine(
            qdrant_url="http://test",
            qdrant_api_key="test",
            gemini_api_key="test"
        )
        
        # Generate with streaming
        context = [{'text': 'test context', 'metadata': {}}]
        generator = engine.generate_answer("test query", context, stream=True)
        
        # Consume generator
        result = "".join(generator)
        
        # Verify
        self.assertEqual(result, "Hello world from Gemini")


class TestScoreNormalization(unittest.TestCase):
    """Additional tests for score normalization edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = HybridSearchEngine(use_reranking=False)
    
    def test_single_document_with_zero_score(self):
        """Test single document with zero score"""
        documents = [
            {'chunk_id': '1', 'text': 'test', 'score': 0.0}
        ]
        
        try:
            results = self.engine.hybrid_search(
                query="test",
                semantic_results=documents,
                top_k=1
            )
            # Should normalize to 0/1 = 0, not crash
            self.assertEqual(len(results), 1)
        except ZeroDivisionError:
            self.fail("Division by zero with single zero-score document")
    
    def test_very_small_scores(self):
        """Test with very small scores (potential numerical issues)"""
        documents = [
            {'chunk_id': '1', 'text': 'test', 'score': 0.0001},
            {'chunk_id': '2', 'text': 'test2', 'score': 0.0002},
        ]
        
        try:
            results = self.engine.hybrid_search(
                query="test",
                semantic_results=documents,
                top_k=2
            )
            self.assertEqual(len(results), 2)
            # Scores should be normalized
            for result in results:
                self.assertGreaterEqual(result.get('hybrid_score', -1), 0)
                self.assertLessEqual(result.get('hybrid_score', 2), 1)
        except Exception as e:
            self.fail(f"Failed with small scores: {e}")


if __name__ == '__main__':
    unittest.main()

