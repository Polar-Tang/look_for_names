import json
import os
from greyhat_api import query_files
from pdf_processing import download_pdf, extract_text_with_tesseract, analyze_pdf_content

# Define constants
OUTPUT_FILE = "results.json"

def main():
    skipped_files = []
    session_cookie = "YOUR_PHP_ID"
    keywords = ["cross border"]
    extensions = ["pdf"]
    start = 0
    limit = 1000
    results = []

    print("Querying Greyhat API...")
    files = query_files(session_cookie, " ".join(keywords), extensions, start=start, limit=limit)
    if not files:
        print("No results found.")
        return

    # Process each file
    for file_info in files:
        url = file_info["url"]
        print(f"Processing file: {url}")

        pdf_file = download_pdf(url)
        if not pdf_file:
            print(f"Skipping file due to download failure: {url}")
            continue

        text = extract_text_with_tesseract(pdf_file, timeout=30)
        if not text:
            print(f"Skipping file due to OCR timeout: {url}")
            continue
        keyword_counts = analyze_pdf_content(text, keywords)


        print(f"Skipped files: {len(skipped_files)}")
        results.append({
            "file": file_info,
            "keywords": keyword_counts
        })

        # Save incrementally to avoid data loss
        with open(OUTPUT_FILE, "w") as outfile:
            json.dump(results, outfile, indent=4)

    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
