"""
This module provides utility functions for handling API requests.

Functions:
- fetch_embedding: Sends a request to the OLLAMA API to fetch embeddings.
"""

import requests

def fetch_embedding(url, model, text):
    """
    Fetches an embedding for the given text using the specified API.

    Args:
        url (str): The API endpoint URL.
        model (str): The model to use for generating embeddings.
        text (str): The input text to embed.

    Returns:
        list: The embedding vector.

    Raises:
        Exception: If the API request fails.
    """
    payload = {"model": model, "prompt": text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception(f"Failed to fetch embedding: {response.text}")
