from neo4j import GraphDatabase
import requests
import json

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test1234"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"  # Embedding model

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_embedding(text):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": text
    }
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

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
    with driver.session() as session:
        result = session.run("MATCH (l:Law) RETURN l.number, l.text")
        for record in result:
            number = record["l.number"]
            text = record["l.text"]
            embedding = get_embedding(text)
            session.execute_write(add_embedding, number, embedding)
            print(f"✅ Embedded {number}")

if __name__ == "__main__":
    main()