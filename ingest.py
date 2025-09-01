import os
import fitz
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

VECTOR_STORE = "vector_store/index.faiss"
META_FILE = "vector_store/meta.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
PDF_FOLDER = "data"

embedder = SentenceTransformer(MODEL_NAME)

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])

def chunk_text(text: str, size=CHUNK_SIZE):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

def build_vector_db():
    texts, metas = [], []

    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(PDF_FOLDER, filename)
            text = extract_text_from_pdf(pdf_path)
            for chunk in chunk_text(text):
                texts.append(chunk)
                metas.append({"file": filename, "content": chunk})

    if not texts:
        print("❌ No PDFs found in data/ folder.")
        return

    embeddings = embedder.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, VECTOR_STORE)

    with open(META_FILE, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m) + "\n")

    print(f"✅ Vector DB built with {len(texts)} chunks from {len(set(m['file'] for m in metas))} PDFs.")

if __name__ == "__main__":
    build_vector_db()
