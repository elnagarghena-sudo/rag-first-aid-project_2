import streamlit as st
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from sentence_transformers import SentenceTransformer
import requests

st.set_page_config(page_title="First Aid Book Assistant")
st.title("First Aid Book Assistant")

# Read the API key from environment variable first (for local testing)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

# When deployed, read from Streamlit secrets instead
try:
    if not OPENROUTER_API_KEY:
        OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
        OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", OPENROUTER_MODEL)
except Exception:
    pass

@st.cache_resource
def load_model():
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

@st.cache_resource
def load_collection():
    client = chromadb.PersistentClient(path="./chroma_store")
    return client.get_or_create_collection(name="first_aid_book")

model = load_model()
collection = load_collection()

def retrieve_context(query, n_results=3):
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=n_results)
    return results["documents"][0]

def build_prompt(question, context_chunks):
    context_text = "\n\n".join(context_chunks)
    return f"""Answer the question based only on the context below.
If the answer is not in the context, say you don't know.
Always mention which part of the context you used.

Context:
{context_text}

Question: {question}

Answer:"""

def ask_ai(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]

question = st.text_input("Ask a question about the book:")

if st.button("Ask") and question:
    with st.spinner("Searching the book..."):
        context_chunks = retrieve_context(question)
        prompt = build_prompt(question, context_chunks)
        answer = ask_ai(prompt)
    st.write(answer)