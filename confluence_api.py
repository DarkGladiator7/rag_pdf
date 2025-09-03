import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# 🔑 Load environment variables
load_dotenv()

CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")  # e.g. https://yourcompany.atlassian.net/wiki
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")  # your Atlassian email
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")  # API token from Atlassian
SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY", "DOCS")  # default = DOCS

AUTH = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


# -----------------------
# 📎 Fetch PDF attachments
# -----------------------
def list_pdfs_in_space(space_key=SPACE_KEY, limit=50):
    """List all PDF attachments in the given Confluence space."""
    url = f"{CONFLUENCE_URL}/rest/api/content"
    params = {"spaceKey": space_key, "limit": limit}
    response = requests.get(url, auth=AUTH, params=params)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to list pages: {response.text}")

    pages = response.json().get("results", [])
    pdf_links = []

    for page in pages:
        page_id = page["id"]
        attach_url = f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment"
        attach_resp = requests.get(attach_url, auth=AUTH)

        if attach_resp.status_code == 200:
            attachments = attach_resp.json().get("results", [])
            for att in attachments:
                if att["title"].lower().endswith(".pdf"):
                    download_link = att["_links"]["download"]
                    pdf_links.append({
                        "title": att["title"],
                        "url": f"{CONFLUENCE_URL}{download_link}"
                    })
    return pdf_links


def download_all_pdfs():
    """Download all PDF attachments in the space to ./data/ folder."""
    pdfs = list_pdfs_in_space()
    downloaded_files = []
    for pdf in pdfs:
        response = requests.get(pdf["url"], auth=AUTH, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(DATA_DIR, pdf["title"])
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            downloaded_files.append(file_path)
            print(f"✅ Downloaded: {pdf['title']}")
        else:
            print(f"❌ Failed to download {pdf['title']}: {response.text}")
    return downloaded_files


# -----------------------
# 📄 Fetch page content
# -----------------------
def fetch_all_page_texts(space_key=SPACE_KEY, limit=50):
    """Fetch plain text content from all pages in the space."""
    url = f"{CONFLUENCE_URL}/rest/api/content"
    params = {"spaceKey": space_key, "limit": limit, "expand": "body.storage"}
    response = requests.get(url, auth=AUTH, params=params)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch pages: {response.text}")

    pages = response.json().get("results", [])
    results = []

    for page in pages:
        title = page["title"]
        html = page["body"]["storage"]["value"]
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        results.append({
            "title": title,
            "content": text.strip()
        })

    return results


# -----------------------
# 🧪 Quick test
# -----------------------
if __name__ == "__main__":
    print("🔎 Testing Confluence API connection...")

    try:
        pages = fetch_all_page_texts(limit=5)
        print(f"✅ Connected! Found {len(pages)} pages in space '{SPACE_KEY}'")
        for p in pages:
            print(f" - {p['title']} (first 100 chars: {p['content'][:100]})")
    except Exception as e:
        print("❌ Error:", e)
