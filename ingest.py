import os
import sys
import shutil
import fitz
import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from confluence_api import download_all_pdfs, fetch_all_page_texts

VECTOR_STORE = "vector_store/index.faiss"
META_FILE = "vector_store/meta.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
PDF_FOLDER_LOCAL = "datalocal"   # local PDFs
PDF_FOLDER_CONF = "data"         # downloaded Confluence PDFs

embedder = SentenceTransformer(MODEL_NAME)

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join([page.get_text("text") for page in doc])

def chunk_text(text: str, size=CHUNK_SIZE):
    words = text.split()
    for i in range(0, len(words), size):
        yield " ".join(words[i:i+size])

def build_vector_db(source="local"):
    texts, metas = [], []

    # ✅ Local PDFs only
    if source == "local":
        if os.path.exists(PDF_FOLDER_LOCAL):
            for filename in os.listdir(PDF_FOLDER_LOCAL):
                if filename.endswith(".pdf"):
                    pdf_path = os.path.join(PDF_FOLDER_LOCAL, filename)
                    text = extract_text_from_pdf(pdf_path)
                    for chunk in chunk_text(text):
                        texts.append(chunk)
                        metas.append({
                            "file": filename,
                            "content": chunk,
                            "source_type": "local_pdf"
                        })
            print(f"✅ Processed local PDFs from '{PDF_FOLDER_LOCAL}'")
        else:
            print("⚠️ No local PDF folder found.")

    # ✅ Confluence PDFs only
    elif source == "pdf":
        # Clear old files
        if os.path.exists(PDF_FOLDER_CONF):
            shutil.rmtree(PDF_FOLDER_CONF)
        os.makedirs(PDF_FOLDER_CONF, exist_ok=True)

        print("🔎 Downloading fresh PDFs from Confluence...")
        pdfs = download_all_pdfs()
        print(f"✅ Downloaded {len(pdfs)} PDFs into '{PDF_FOLDER_CONF}'")
        for pdf_path in pdfs:
            text = extract_text_from_pdf(pdf_path)
            for chunk in chunk_text(text):
                texts.append(chunk)
                metas.append({
                    "file": os.path.basename(pdf_path),
                    "content": chunk,
                    "source_type": "confluence_pdf"
                })

    # ✅ Confluence Pages only
    elif source == "pages":
        print("🔎 Fetching Confluence pages...")
        pages = fetch_all_page_texts()
        print(f"✅ Retrieved {len(pages)} pages from Confluence")
        for page in pages:
            for chunk in chunk_text(page["content"]):
                texts.append(chunk)
                metas.append({
                    "file": page["title"],
                    "content": chunk,
                    "source_type": "confluence_page"
                })

    # ✅ Both PDFs + Pages
    elif source == "both":
        # Clear old files
        if os.path.exists(PDF_FOLDER_CONF):
            shutil.rmtree(PDF_FOLDER_CONF)
        os.makedirs(PDF_FOLDER_CONF, exist_ok=True)

        # PDFs from Confluence
        print("🔎 Downloading fresh PDFs from Confluence...")
        pdfs = download_all_pdfs()
        print(f"✅ Downloaded {len(pdfs)} PDFs into '{PDF_FOLDER_CONF}'")
        for pdf_path in pdfs:
            text = extract_text_from_pdf(pdf_path)
            for chunk in chunk_text(text):
                texts.append(chunk)
                metas.append({
                    "file": os.path.basename(pdf_path),
                    "content": chunk,
                    "source_type": "confluence_pdf"
                })

        # Pages
        print("🔎 Fetching Confluence pages...")
        pages = fetch_all_page_texts()
        print(f"✅ Retrieved {len(pages)} pages from Confluence")
        for page in pages:
            for chunk in chunk_text(page["content"]):
                texts.append(chunk)
                metas.append({
                    "file": page["title"],
                    "content": chunk,
                    "source_type": "confluence_page"
                })

    else:
        print(f"❌ Unknown source '{source}'. Use local | pdf | pages | both")
        return

    if not texts:
        print("❌ No content found.")
        return

    # ✅ Embed and store
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

if __name__ == "__main__":
    source = "local"
    if len(sys.argv) > 1 and sys.argv[1].startswith("--source="):
        source = sys.argv[1].split("=")[1]
    build_vector_db(source)
