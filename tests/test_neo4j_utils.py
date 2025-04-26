import unittest
from unittest.mock import patch, MagicMock
from src.database.neo4j_utils import Neo4jConnection

class TestNeo4jConnection(unittest.TestCase):
    @patch("src.database.neo4j_utils.GraphDatabase.driver")
    def test_query_success(self, mock_driver):
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value = mock_session
        mock_session.run.return_value = "Query Result"

        conn = Neo4jConnection()
        result = conn.query("MATCH (n) RETURN n")
        self.assertEqual(result, "Query Result")
        conn.close()

    @patch("src.database.neo4j_utils.GraphDatabase.driver")
    def test_query_failure(self, mock_driver):
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value = mock_session
        mock_session.run.side_effect = Exception("Query Error")

        conn = Neo4jConnection()
        with self.assertRaises(Exception):
            conn.query("MATCH (n) RETURN n")
        conn.close()

if __name__ == "__main__":
    unittest.main()