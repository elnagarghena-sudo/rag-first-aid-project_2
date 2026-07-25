# Load the cleaned text produced by 02_preprocessing.py
with open("cleaned_book_text.txt", "r", encoding="utf-8") as f:
    cleaned_text = f.read()

print(f"Loaded text length: {len(cleaned_text)} characters")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start += chunk_size - overlap
    return chunks

# Split the cleaned text into overlapping chunks
chunks = chunk_text(cleaned_text, chunk_size=500, overlap=50)
print(f"Total chunks created: {len(chunks)}")

# Save the chunks to a file so later steps can reuse them
with open("chunks.txt", "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks):
        f.write(f"\n--- Chunk {i} ---\n")
        f.write(chunk)

print("Saved chunks.txt successfully!")