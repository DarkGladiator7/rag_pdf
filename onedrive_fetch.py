
import os
import requests
from dotenv import load_dotenv
from onedrive_api import list_pdfs_in_folder

load_dotenv()
SAVE_DIR = "data"

def download_all_pdfs():
    os.makedirs(SAVE_DIR, exist_ok=True)
    pdfs = list_pdfs_in_folder()
    for pdf in pdfs:
        path = os.path.join(SAVE_DIR, pdf["name"])
        if not os.path.exists(path):  # Skip already downloaded
            resp = requests.get(pdf["url"])
            if resp.status_code == 200:
                with open(path, "wb") as f:
                    f.write(resp.content)
                print(f"✅ Downloaded: {path}")
            else:
                print(f"❌ Failed: {pdf['name']}")
    return [os.path.join(SAVE_DIR, f) for f in os.listdir(SAVE_DIR) if f.endswith(".pdf")]

if __name__ == "__main__":
    download_all_pdfs()
