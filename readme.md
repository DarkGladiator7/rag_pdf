# 📚 RAG PDF Search with Groq LLaMA

This project lets you ask questions about your **local PDF files** using a **RAG (Retrieval-Augmented Generation) pipeline**.  
PDFs are parsed, chunked, embedded into a vector database (FAISS), and queried with Groq’s LLaMA model.

---

## 🚀 Setup

```bash
# 1. Clone project (or copy files)
git clone <your-repo-url>
cd rag_pdf_groq

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add environment variables
echo "GROQ_API_KEY=your_api_key_here" > .env
📂 Project Structure
pgsql
Copy code
rag_pdf_groq/
├── data/                # Put your PDF files here
├── vector_store/        # Auto-generated FAISS index + metadata
├── ingest.py            # Build vector DB from PDFs
├── retriever.py         # Search chunks from FAISS
├── llm.py               # Wrapper for Groq API
├── main.py              # RAG query entry point
├── requirements.txt
└── README.md
🛠 Usage
1. Add PDFs
Place all your PDF files inside the data/ folder.

2. Build the vector DB
bash
Copy code
python ingest.py
