import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from src.retriever.backend_retriever import cosine_similarity, retrieve_similar_laws, get_embedding

class TestBackendRetriever(unittest.TestCase):
    def test_cosine_similarity(self):
        # Test with aligned vectors
        vec1 = [1, 0, 0, 0]
        vec2 = [1, 0, 0, 0]
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), 1.0)

        # Test with perpendicular vectors
        vec1 = [1, 0, 0, 0]
        vec2 = [0, 1, 0, 0]
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), 0.0)

        # Test with opposite vectors
        vec1 = [1, 0, 0, 0]
        vec2 = [-1, 0, 0, 0]
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), -1.0)

        # Test with real-valued vectors
        vec1 = [0.5, 0.5, 0.5, 0.5]
        vec2 = [0.1, 0.2, 0.3, 0.4]
        expected = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        self.assertAlmostEqual(cosine_similarity(vec1, vec2), expected)

    @patch('src.retriever.backend_retriever.get_embedding')
    @patch('src.retriever.backend_retriever.Neo4jConnection')
    def test_retrieve_similar_laws(self, mock_neo4j, mock_get_embedding):
        # Setup mock embedding function
        mock_get_embedding.return_value = [0.1, 0.2, 0.3, 0.4]
        
        # Setup mock database results
        mock_result = [
            {"l.number": "Art 1", "l.text": "First law", "l.embedding": [0.9, 0.1, 0.1, 0.1]},
            {"l.number": "Art 2", "l.text": "Second law", "l.embedding": [0.1, 0.9, 0.1, 0.1]},
            {"l.number": "Art 3", "l.text": "Third law", "l.embedding": [0.1, 0.2, 0.3, 0.4]},
            {"l.number": "Art 4", "l.text": "Fourth law", "l.embedding": [0.4, 0.3, 0.2, 0.1]},
        ]
        
        mock_neo4j_instance = mock_neo4j.return_value.__enter__.return_value
        mock_neo4j_instance.query.return_value = mock_result

        # Test function
        results = retrieve_similar_laws("test query", top_k=2)
        
        # Art 3 should be the closest match because it has identical embedding
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][1], "Art 3")  # First result should be Art 3
        self.assertAlmostEqual(results[0][0], 1.0)  # Perfect similarity
        
    @patch('src.retriever.backend_retriever.fetch_embedding')
    def test_get_embedding(self, mock_fetch):
        mock_fetch.return_value = [0.1, 0.2, 0.3]
        
        result = get_embedding("test text")
        
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_fetch.assert_called_once()

    @patch('src.retriever.backend_retriever.Neo4jConnection')
    @patch('src.retriever.backend_retriever.get_embedding')
    def test_retrieve_similar_laws_exception(self, mock_get_embedding, mock_neo4j):
        # Test error handling
        mock_get_embedding.side_effect = Exception("Test exception")
        
        with self.assertRaises(Exception):
            retrieve_similar_laws("test query")
            
if __name__ == '__main__':
    unittest.main()
