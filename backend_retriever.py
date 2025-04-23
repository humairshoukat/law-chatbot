from neo4j import GraphDatabase
import numpy as np
import requests

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test1234"

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "nomic-embed-text"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_embedding(text):
    payload = {"model": OLLAMA_MODEL, "prompt": text}
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception("Failed to get embedding")

def cosine_similarity(vec1, vec2):
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def retrieve_similar_laws(query, top_k=3):
    query_embedding = get_embedding(query)
    
    with driver.session() as session:
        result = session.run("MATCH (l:Law) RETURN l.number, l.text, l.embedding")
        scored = []
        for record in result:
            if record["l.embedding"]:
                score = cosine_similarity(query_embedding, record["l.embedding"])
                scored.append((score, record["l.number"], record["l.text"]))
        
        scored.sort(reverse=True)
        return scored[:top_k]

if __name__ == "__main__":
    query = input("Enter your query: ")
    results = retrieve_similar_laws(query)
    for score, number, text in results:
        print(f"[{score:.2f}] {number}: {text}")
