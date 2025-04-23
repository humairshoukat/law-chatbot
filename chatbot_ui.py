import streamlit as st
from backend_retriever import retrieve_similar_laws  # Use the RAG code

st.title("📚 Law Chatbot (Neo4j + Ollama)")

query = st.text_input("Ask about the law...")

if st.button("Search"):
    if query:
        results = retrieve_similar_laws(query)
        for score, number, text in results:
            st.markdown(f"### Section {number}")
            st.markdown(f"**Similarity**: {score:.2f}")
            st.markdown(f"> {text}")
            st.markdown("---")
    else:
        st.warning("Please enter a query!")
