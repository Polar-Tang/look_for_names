import json
import asyncio
from greyhat_api import query_files
from pdf_processing import download_pdf_async, extract_text_with_tesseract, analyze_pdf_content

# Define constants
OUTPUT_FILE = "results.json"

async def main():
    skipped_files = []
    session_cookie = "fm81ksj89dh2laan4in2k7gbbs"
    keywords = ["cross border"]
    extensions = ["pdf"]
    pdf_keywords = ["mercado libre", "TRADE"]
    results = []

    print("Querying Greyhat API...")
    files = query_files(session_cookie, " ".join(keywords), extensions)
    if not files:
        print("No results found.")
        return

    # Process each file asynchronously
    for file_info in files:
        url = file_info.get("url")
        if not url:
            print(f"Skipping file without URL: {file_info}")
            skipped_files.append(file_info)
            continue

        print(f"Processing file: {url}")

        # Asynchronously download the PDF
        pdf_data = await download_pdf_async(url)
        if not pdf_data:
            print(f"Skipping file due to download failure: {url}")
            skipped_files.append(file_info)
            continue

        # Extract text using Tesseract
        text = extract_text_with_tesseract(pdf_data)
        if not text:
            print(f"Skipping file due to OCR timeout: {url}")
            skipped_files.append(file_info)
            continue

        # Analyze the extracted text
        keyword_counts = analyze_pdf_content(text, pdf_keywords)

        if any(keyword_counts.values()):  # If any PDF keyword is found
            results.append({
                "file": file_info,
                "keywords": keyword_counts
            })
            print(f"Match found in {url}: {keyword_counts}")

        # Save incrementally to avoid data loss
        with open(OUTPUT_FILE, "w") as outfile:
            json.dump(results, outfile, indent=4)

    print(f"Results saved to {OUTPUT_FILE}")
    print(f"Skipped files: {len(skipped_files)}")

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main function
