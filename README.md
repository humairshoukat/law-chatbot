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
