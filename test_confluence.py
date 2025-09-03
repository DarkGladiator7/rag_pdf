from confluence_api import list_pdfs_in_space, download_all_pdfs, SPACE_KEY

print("🔎 Checking for PDF attachments in Confluence...")

try:
    pdfs = list_pdfs_in_space(SPACE_KEY)
    if not pdfs:
        print("⚠️ No PDFs found in space.")
    else:
        print(f"✅ Found {len(pdfs)} PDFs in space '{SPACE_KEY}':")
        for pdf in pdfs:
            print(f" - {pdf['title']} ({pdf['url']})")

        # Optional: try downloading
        print("\n⬇️ Downloading PDFs into ./data/")
        files = download_all_pdfs()
        print(f"✅ Downloaded {len(files)} PDFs into ./data/")
except Exception as e:
    print("❌ Error:", e)
