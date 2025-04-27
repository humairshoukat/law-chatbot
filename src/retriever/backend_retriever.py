"""
This module retrieves similar laws based on a query using embeddings.

Functions:
- get_embedding: Fetches an embedding for a given text using the OLLAMA API.
- cosine_similarity: Computes the cosine similarity between two vectors.
- retrieve_similar_laws: Retrieves the top-k similar laws for a given query.
"""

from config.constants import OLLAMA_URL, OLLAMA_MODEL
from src.database.neo4j_utils import Neo4jConnection
from src.retriever.api_utils import fetch_embedding
import numpy as np
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_embedding(text):
    return fetch_embedding(OLLAMA_URL, OLLAMA_MODEL, text)

def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def retrieve_similar_laws(query, top_k=3):
    try:
        query_embedding = get_embedding(query)
        with Neo4jConnection() as conn:
            result = conn.query("MATCH (l:Law) RETURN l.number, l.text, l.embedding")
            scored = []
            for record in result:
                if record["l.embedding"]:
                    score = cosine_similarity(query_embedding, record["l.embedding"])
                    scored.append((score, record["l.number"], record["l.text"]))
            scored.sort(reverse=True)
            return scored[:top_k]
    except Exception as e:
        logging.error(f"Error retrieving similar laws: {e}")
        raise

if __name__ == "__main__":
    query = input("Enter your query: ")
    results = retrieve_similar_laws(query)
    for score, number, text in results:
        print(f"[{score:.2f}] {number}: {text}")
