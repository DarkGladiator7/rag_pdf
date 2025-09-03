from fastapi import FastAPI, Query
from pydantic import BaseModel
from ingest import build_vector_db
from retriever import search_vector_db
from llm import call_llm
import json

app = FastAPI(title="RAG PDF & Confluence API")

class QueryRequest(BaseModel):
    query: str
    source: str = "both"   # local | pdf | pages | both
    k: int = 5

@app.post("/ingest")
def ingest_endpoint(source: str = Query("both", enum=["local", "pdf", "pages", "both"])):
    """Rebuild vector DB from chosen source."""
    build_vector_db(source)
    return {"status": "✅ Vector DB rebuilt", "source": source}

@app.post("/query")
def query_endpoint(req: QueryRequest):
    """Run RAG query using vector DB + LLM."""
    contexts = search_vector_db(req.query, k=req.k)
    if not contexts:
        return {"answer": "No relevant information found.", "sources": []}

    context_text = "\n\n".join(
        [f"From {c.get('source_type', 'unknown')} - {c['file']}:\n{c['content']}" for c in contexts]
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use provided context. Reply in JSON with keys: 'answer' and 'sources'."},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {req.query}"}
    ]

    try:
        response = call_llm(messages, expect_json=True)
    except Exception as e:
        return {"error": str(e)}

    return response
