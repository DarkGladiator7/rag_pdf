import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer

VECTOR_STORE = "vector_store/index.faiss"
META_FILE = "vector_store/meta.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

embedder = SentenceTransformer(MODEL_NAME)

def search_vector_db(query: str, k=5):
    """Search vector DB and return top-k chunks with metadata."""
    index = faiss.read_index(VECTOR_STORE)

    with open(META_FILE, "r", encoding="utf-8") as f:
        metas = [json.loads(line) for line in f]

    q_emb = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, k)

    results = []
    for idx in I[0]:
        if idx != -1:
            results.append(metas[idx])
    return results
