from llm import call_llm
from retriever import search_vector_db
import json

def agentic_rag_query(user_query: str):
    """Perform retrieval-augmented generation across local + Confluence PDFs."""
    contexts = search_vector_db(user_query, k=5)

    if not contexts:
        return {"answer": "No relevant information found.", "sources": []}

    context_text = "\n\n".join(
        [f"From {c['source_type']} - {c['file']}:\n{c['content']}" for c in contexts]
    )

    messages = [
        {"role": "system", "content": (
            "You are a helpful assistant. Use provided context from Confluence PDFs and local PDFs "
            "to answer the user query. Reply ONLY in valid JSON with keys: 'answer', 'sources'. "
            "Sources must include file name and source type."
        )},
        {"role": "user", "content": f"Context:\n{context_text}\n\nQuestion: {user_query}"}
    ]

    return call_llm(messages, expect_json=True)
