from llm import call_llm
from retriever import search_vector_db
import json

def rag_query(user_query: str):
    contexts = search_vector_db(user_query)
    if not contexts:
        return {"answer": "No relevant information found.", "sources": []}

    context_text = "\n\n".join(
        [f"From {c['source_type']} - {c['file']}:\n{c['content']}" for c in contexts]
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use the provided context to answer the user query. "
                "IMPORTANT: Reply ONLY in valid JSON without backticks, code fences, or extra text. "
                "The JSON must have two keys: 'answer' (string) and 'sources' (list of strings)."
            ),
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion: {user_query}",
        },
    ]
    return call_llm(messages, expect_json=True)

if __name__ == "__main__":
    query = input("Enter your query: ")
    response = rag_query(query)
    print("🔎 Structured Answer:\n", json.dumps(response, indent=2))
