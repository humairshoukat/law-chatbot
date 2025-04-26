# law-chatbot
Law chatbot based on law books, built using neo4j graph database, RAG, ollama, nomic-embed-text model, and streamlit.

## How to Run
1. Create a venv and install all the requirements
2. Download ollama and pull nomic-embed-text model
3. Run neo4j grah databse using docker
4. Place the law files in the law directory
5. Run all the python files in the following sequence:
   - import_laws_to_neo4j.py
   - create_indexes.py
   - generate_embeddings.py
   - chatbot_ui.py  (streamlit run chatbot_ui.py)

## Environment Variables

This project uses a `.env` file to manage sensitive configurations. Below are the required environment variables:

```
# Neo4j configurations
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password

# OLLAMA configurations
OLLAMA_URL=http://localhost:11434/api/embeddings
OLLAMA_MODEL=nomic-embed-text
```

You can use the provided `.env.example` file as a template. Copy it to `.env` and replace the placeholder values with your actual configurations:

```bash
cp .env.example .env
```
