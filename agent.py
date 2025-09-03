import requests
import os
from llm import call_llm

API_URL = "http://127.0.0.1:8000"

def choose_tool(user_input: str):
    """Decide which tool to call based on user input using LLM."""
    messages = [
        {"role": "system", "content": (
            "You are a tool router. Only choose 'ingest' if the user explicitly asks to rebuild or update the database, "
            "otherwise always choose 'query'. "
            "Available tools: ingest, query. "
            "Reply ONLY in JSON with keys: 'tool' (either 'ingest' or 'query') and 'args'. "
            "For 'query', include keys: 'query' (user's input) and optional 'k' (number of results). "
            "For 'ingest', 'args' can be empty."
        )},
        {"role": "user", "content": user_input}
    ]

    try:
        result = call_llm(messages, expect_json=True)

        # Make sure result is a dictionary
        if isinstance(result, str):
            import json
            try:
                result = json.loads(result)
            except:
                print("⚠️ LLM returned non-JSON, defaulting to query")
                result = {"tool": "query", "args": {"query": user_input, "k": 5}}

        # Ensure keys exist
        if "tool" not in result or "args" not in result:
            result = {"tool": "query", "args": {"query": user_input, "k": 5}}

        return result

    except Exception as e:
        print("❌ Tool routing failed:", e)
        return {"tool": "query", "args": {"query": user_input, "k": 5}}

def run_agent():
    print("🤖 Agent connected to RAG API with tool routing! (type 'exit' to quit)\n")

    while True:
        user_input = input("❓ Ask a question or give a command: ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        decision = choose_tool(user_input)

        # Ensure decision is a dictionary
        if not isinstance(decision, dict):
            print("⚠️ Invalid tool decision, defaulting to query")
            decision = {"tool": "query", "args": {"query": user_input, "k": 5}}

        tool = decision.get("tool", "query")
        args = decision.get("args", {})

        try:
            if tool == "ingest":
                # Always ingest from both sources
                print("🔄 Running ingest with source='both'...")
                resp = requests.post(f"{API_URL}/ingest", params={"source": "both"})

            elif tool == "query":
                # Ensure query key exists
                query_text = user_input
                k = args.get("k", 5)
                print(f"🔍 Running query='{query_text}' (top {k} results)...")
                resp = requests.post(f"{API_URL}/query", json={"query": query_text, "source": "both", "k": k})

            else:
                print(f"⚠️ Unknown tool '{tool}', defaulting to query.")
                resp = requests.post(f"{API_URL}/query", json={"query": user_input, "source": "both", "k": 5})

            # Handle response
            if resp.status_code != 200:
                print("❌ API Error:", resp.text)
                continue

            result = resp.json()
            print("\n🔎 Agent Result:\n", result, "\n")

        except Exception as e:
            print("❌ Exception occurred while calling API:", e)



if __name__ == "__main__":
    run_agent()
