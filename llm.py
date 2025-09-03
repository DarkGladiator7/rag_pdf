import os
import requests
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ Missing GROQ_API_KEY in .env file")

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def call_llm(messages, temperature=0.3, expect_json=False):
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        raise Exception(f"❌ LLM Error: {response.status_code} - {response.text}")

    content = response.json()["choices"][0]["message"]["content"].strip()

    if expect_json:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
        except Exception:
            raise ValueError(f"❌ Failed to parse JSON: {content}")

    return content
