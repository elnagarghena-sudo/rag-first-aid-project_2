import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import re
import numpy as np
import chromadb

# Load the chunks produced by 03_chunking.py
with open("chunks.txt", "r", encoding="utf-8") as f:
    raw_chunks_file = f.read()

parts = re.split(r"--- Chunk \d+ ---\n", raw_chunks_file)
chunks = [p.strip() for p in parts if p.strip() != ""]

# Load the embeddings produced by 04_vector_representation.py
embeddings = np.load("embeddings.npy")

print(f"Loaded {len(chunks)} chunks and {len(embeddings)} embeddings")

# Create a persistent Chroma client (saves data to disk)
client = chromadb.PersistentClient(path="./chroma_store")

# Create or get the collection to store our chunks
collection = client.get_or_create_collection(name="first_aid_book")

# Assign a unique ID to each chunk
ids = [f"chunk_{i}" for i in range(len(chunks))]

# Add chunks with their embeddings and IDs into the collection
collection.add(
    documents=chunks,
    embeddings=embeddings.tolist(),
    ids=ids
)

print(f"Total items stored in Chroma: {collection.count()}")