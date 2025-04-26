"""
This module generates embeddings for laws stored in the Neo4j database.

Functions:
- get_embedding: Fetches an embedding for a given text using the OLLAMA API.
- add_embedding: Adds an embedding to a law node in the database.
- main: Main function to orchestrate the embedding generation process.
"""

from src.database.neo4j_utils import Neo4jConnection
from config.constants import OLLAMA_URL, OLLAMA_MODEL
from src.retriever.api_utils import fetch_embedding
import requests
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_embedding(text):
    return fetch_embedding(OLLAMA_URL, OLLAMA_MODEL, text)

def add_embedding(tx, number, embedding):
    tx.run(
        """
        MATCH (l:Law {number: $number})
        SET l.embedding = $embedding
        """,
        number=number,
        embedding=embedding
    )

def main():
    try:
        with Neo4jConnection() as conn:
            result = conn.query("MATCH (l:Law) RETURN l.number, l.text")
            for record in result:
                number = record["l.number"]
                text = record["l.text"]
                embedding = get_embedding(text)
                conn.execute_write(add_embedding, number, embedding)
                logging.info(f"✅ Embedded {number}")
    except Exception as e:
        logging.error(f"Error in embedding generation: {e}")

if __name__ == "__main__":
    main()