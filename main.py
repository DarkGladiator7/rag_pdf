from rag_pipeline import agentic_rag_query
import json

if __name__ == "__main__":
    query = input("Enter your query: ")
    response = agentic_rag_query(query)
    print("🔎 Structured Answer:\n", json.dumps(response, indent=2))
