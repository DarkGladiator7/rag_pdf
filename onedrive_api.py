import os
import base64
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("MS_CLIENT_ID")
CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
TENANT_ID = os.getenv("MS_TENANT_ID")
SHARED_LINK = os.getenv("ONEDRIVE_SHARED_LINK")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]

def get_access_token():
    """Authenticate via MSAL and return a Graph API token."""
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_silent(SCOPE, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" not in result:
        raise Exception(f"❌ Failed to get token: {result}")
    return result["access_token"]

def decode_shared_url(shared_url: str) -> str:
    """Convert OneDrive share URL into Graph API encoded form."""
    base = base64.urlsafe_b64encode(shared_url.encode("utf-8")).decode("utf-8")
    return base.strip("=")

def list_pdfs_in_folder():
    """List all PDFs in the shared folder with download URLs."""
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    encoded = decode_shared_url(SHARED_LINK)

    url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/children"
    resp = requests.get(url, headers=headers)

    if resp.status_code != 200:
        raise Exception(f"❌ Graph API error: {resp.status_code} {resp.text}")

    items = resp.json().get("value", [])
    pdfs = [
        {"name": item["name"], "url": item["@microsoft.graph.downloadUrl"]}
        for item in items
        if item["name"].lower().endswith(".pdf")
    ]
    return pdfs
