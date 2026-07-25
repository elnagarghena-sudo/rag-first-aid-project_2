import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model (must match the one used to build the store)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Connect to the existing Chroma store created by 05_create_chroma_store.py
client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection(name="first_aid_book")

def retrieve_context(query, n_results=3):
    # Convert the user's question into an embedding using the same model
    query_embedding = model.encode([query]).tolist()
    
    # Search Chroma for the most similar chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    
    return results["documents"][0]

# Test the retrieval with a sample question
if __name__ == "__main__":
    test_question = "ما هي أعراض الكسر؟"
    retrieved_chunks = retrieve_context(test_question)
    
    for i, chunk in enumerate(retrieved_chunks):
        print(f"--- Result {i+1} ---")
        print(chunk[:300])
        print()