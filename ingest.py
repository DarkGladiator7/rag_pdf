# ingest.py
import os
import sys
import fitz
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from confluence_api import download_all_pdfs

VECTOR_STORE = "vector_store/index.faiss"
META_FILE = "vector_store/meta.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunking params
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# Folders
PDF_FOLDER_LOCAL = "datalocal"   # Local PDFs
PDF_FOLDER_CONF = "data"         # Downloaded Confluence PDFs

embedder = SentenceTransformer(MODEL_NAME)


# ----------------------
# 🔹 PDF Text Extractor
# ----------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])


# ----------------------
# 🔹 Chunking with Overlap
# ----------------------
def chunk_text(text: str, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    i = 0
    while i < len(words):
        yield " ".join(words[i:i + size])
        i += size - overlap


# ----------------------
# 🔹 Build Vector DB
# ----------------------
def build_vector_db(source="local"):
    texts, metas = [], []

    # ✅ Local PDFs
    if source == "local":
        if os.path.exists(PDF_FOLDER_LOCAL):
            for filename in os.listdir(PDF_FOLDER_LOCAL):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(PDF_FOLDER_LOCAL, filename)
                    text = extract_text_from_pdf(pdf_path)
                    for chunk in chunk_text(text):
                        texts.append(chunk)
                        metas.append({
                            "source_type": "local_pdf",
                            "file": filename,
                            "content": chunk
                        })
            print(f"✅ Processed local PDFs from '{PDF_FOLDER_LOCAL}'")
        else:
            print("⚠️ No local PDF folder found.")

    # ✅ Confluence PDFs
    elif source == "pdf":
        print("🔎 Downloading fresh PDFs from Confluence...")
        pdfs = download_all_pdfs()
        print(f"✅ Downloaded {len(pdfs)} PDFs into '{PDF_FOLDER_CONF}'")
        for pdf_path in pdfs:
            text = extract_text_from_pdf(pdf_path)
            for chunk in chunk_text(text):
                texts.append(chunk)
                metas.append({
                    "source_type": "confluence_pdf",
                    "file": os.path.basename(pdf_path),
                    "content": chunk
                })

    # ✅ Both local + Confluence PDFs
    elif source == "both":
        # Local PDFs
        if os.path.exists(PDF_FOLDER_LOCAL):
            for filename in os.listdir(PDF_FOLDER_LOCAL):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(PDF_FOLDER_LOCAL, filename)
                    text = extract_text_from_pdf(pdf_path)
                    for chunk in chunk_text(text):
                        texts.append(chunk)
                        metas.append({
                            "source_type": "local_pdf",
                            "file": filename,
                            "content": chunk
                        })
            print(f"✅ Processed local PDFs from '{PDF_FOLDER_LOCAL}'")

        # Confluence PDFs
        print("🔎 Downloading fresh PDFs from Confluence...")
        pdfs = download_all_pdfs()
        print(f"✅ Downloaded {len(pdfs)} PDFs into '{PDF_FOLDER_CONF}'")
        for pdf_path in pdfs:
            text = extract_text_from_pdf(pdf_path)
            for chunk in chunk_text(text):
                texts.append(chunk)
                metas.append({
                    "source_type": "confluence_pdf",
                    "file": os.path.basename(pdf_path),
                    "content": chunk
                })

    else:
        print(f"❌ Unknown source '{source}'. Use local | pdf | both")
        return

    if not texts:
        print("❌ No content found.")
        return

    # ✅ Encode & Store in FAISS
    embeddings = embedder.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    os.makedirs("vector_store", exist_ok=True)
    faiss.write_index(index, VECTOR_STORE)

    with open(META_FILE, "w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m) + "\n")

    print(f"✅ Vector DB built with {len(texts)} chunks from source: {source}")


# ----------------------
# 🔹 CLI Runner
# ----------------------
if __name__ == "__main__":
    source = "local"
    if len(sys.argv) > 1 and sys.argv[1].startswith("--source="):
        source = sys.argv[1].split("=")[1]
    build_vector_db(source)
