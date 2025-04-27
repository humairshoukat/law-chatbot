import unittest
from unittest.mock import patch, MagicMock
from src.database.neo4j_utils import Neo4jConnection

class TestNeo4jConnection(unittest.TestCase):
    @patch("src.database.neo4j_utils.GraphDatabase.driver")
    def test_query_success(self, mock_driver):
        # Create a mock for the session and its run method
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Create a mock result that will be returned by session.run()
        mock_result = MagicMock()
        mock_session.run.return_value = mock_result

        # Test the query method
        conn = Neo4jConnection()
        result = conn.query("MATCH (n) RETURN n")
        
        # Verify that we get back the mock result object
        self.assertEqual(result, mock_result)
        
        # Verify that run was called with the correct query
        mock_session.run.assert_called_once_with("MATCH (n) RETURN n", None)
        
        conn.close()

    @patch("src.database.neo4j_utils.GraphDatabase.driver")
    def test_query_failure(self, mock_driver):
        # Setup mock session to raise an exception when run is called
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
        mock_session.run.side_effect = Exception("Query Error")

        # Test that an exception is raised when query fails
        conn = Neo4jConnection()
        with self.assertRaises(Exception):
            conn.query("MATCH (n) RETURN n")
        conn.close()

if __name__ == "__main__":
    unittest.main()