import unittest
from unittest.mock import patch, MagicMock, call
from src.embeddings.generate_embeddings import get_embedding, add_embedding, main

class TestEmbeddingsGeneration(unittest.TestCase):
    @patch('src.embeddings.generate_embeddings.fetch_embedding')
    def test_get_embedding(self, mock_fetch):
        # Setup mock return value
        mock_fetch.return_value = [0.1, 0.2, 0.3]
        
        # Call the function
        result = get_embedding("test text")
        
        # Verify results
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_fetch.assert_called_once()
        
    def test_add_embedding(self):
        # Create mock transaction
        mock_tx = MagicMock()
        
        # Call the function
        add_embedding(mock_tx, "Article 1", [0.1, 0.2, 0.3])
        
        # Verify the transaction was called with correct parameters
        mock_tx.run.assert_called_once()
        args, kwargs = mock_tx.run.call_args
        self.assertIn("MATCH (l:Law {number: $number})", args[0])
        self.assertIn("SET l.embedding = $embedding", args[0])
        self.assertEqual(kwargs["number"], "Article 1")
        self.assertEqual(kwargs["embedding"], [0.1, 0.2, 0.3])
        
    @patch('src.embeddings.generate_embeddings.Neo4jConnection')
    @patch('src.embeddings.generate_embeddings.get_embedding')
    def test_main_success(self, mock_get_embedding, mock_neo4j):
        # Setup mock database connection and results
        mock_neo4j_instance = mock_neo4j.return_value.__enter__.return_value
        mock_neo4j_instance.query.return_value = [
            {"l.number": "Article 1", "l.text": "First law"},
            {"l.number": "Article 2", "l.text": "Second law"}
        ]
        
        # Setup mock embedding function
        mock_get_embedding.side_effect = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        # Call the main function
        main()
        
        # Verify database was queried
        mock_neo4j_instance.query.assert_called_once_with("MATCH (l:Law) RETURN l.number, l.text")
        
        # Verify get_embedding was called for each law
        mock_get_embedding.assert_has_calls([
            call("First law"),
            call("Second law")
        ])
        
        # Verify execute_write was called for each law
        self.assertEqual(mock_neo4j_instance.execute_write.call_count, 2)
        
    @patch('src.embeddings.generate_embeddings.Neo4jConnection')
    @patch('src.embeddings.generate_embeddings.logging.error')
    def test_main_exception(self, mock_logging, mock_neo4j):
        # Setup mock to raise exception
        mock_neo4j.return_value.__enter__.side_effect = Exception("Database error")
        
        # Call the main function
        main()
        
        # Verify error was logged
        mock_logging.assert_called_once()
        args, _ = mock_logging.call_args
        self.assertIn("Error in embedding generation", args[0])
        self.assertIn("Database error", args[0])
        
if __name__ == '__main__':
    unittest.main()
