import unittest
from unittest.mock import patch
from src.retriever.api_utils import fetch_embedding

class TestAPIUtils(unittest.TestCase):
    @patch("src.retriever.api_utils.requests.post")
    def test_fetch_embedding_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"embedding": [0.1, 0.2, 0.3]}

        result = fetch_embedding("http://example.com", "test-model", "test-text")
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch("src.retriever.api_utils.requests.post")
    def test_fetch_embedding_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        mock_post.return_value.text = "Internal Server Error"

        with self.assertRaises(Exception) as context:
            fetch_embedding("http://example.com", "test-model", "test-text")
        self.assertIn("Failed to fetch embedding", str(context.exception))

if __name__ == "__main__":
    unittest.main()