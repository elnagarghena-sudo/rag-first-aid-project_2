import streamlit as st
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import zipfile
import glob

if os.path.exists("chroma_store.zip") and not os.path.exists("chroma_store_extracted"):
    with zipfile.ZipFile("chroma_store.zip", "r") as zip_ref:
        zip_ref.extractall("chroma_store_extracted")

def find_chroma_path():
    candidates = glob.glob("**/chroma.sqlite3", recursive=True)
    if not candidates:
        return "./chroma_store"
    best = max(candidates, key=lambda p: os.path.getsize(p))
    folder = os.path.dirname(os.path.abspath(best))
    return folder if folder != "" else "."

CHROMA_PATH = find_chroma_path()
import chromadb
from sentence_transformers import SentenceTransformer
import requests

st.set_page_config(page_title="First Aid Book Assistant")
st.title("First Aid Book Assistant")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

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
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name="first_aid_book")

model = load_model()
collection = load_collection()

st.write(f"Debug - Chroma path used: {CHROMA_PATH}")
st.write(f"Debug - items in collection: {collection.count()}")

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
