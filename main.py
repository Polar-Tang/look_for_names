import json
import asyncio
from greyhat_api import query_files
from pdf_processing import download_pdf_async, extract_text_with_tesseract, analyze_pdf_content
import aiohttp

# Define constants
OUTPUT_FILE = "results.json"

async def process_file(file_info, session, pdf_keywords, semaphore):
    async with semaphore:  # Limit the number of concurrent downloads
        url = file_info.get("url")
        if not url:
            print(f"Skipping file without URL: {file_info}")
            return None

        print(f"Processing file: {url}")
        pdf_data = await download_pdf_async(url, session)
        if not pdf_data:
            print(f"Skipping file due to download failure: {url}")
            return None

        text = extract_text_with_tesseract(pdf_data)
        if not text:
            print(f"Skipping file due to OCR timeout: {url}")
            return None

        keyword_counts = analyze_pdf_content(text, pdf_keywords)
        if any(keyword_counts.values()):
            print(f"Match found in {url}: {keyword_counts}")
            return {"file": file_info, "keywords": keyword_counts}
        return None

async def main():
    skipped_files = []
    session_cookie = "63upadftsgjdt328kdlkbcrq8d"
    keywords = ["cross border"]
    extensions = ["pdf"]
    pdf_keywords = ["mercado libre", "TRADE"]
    results = []

    files = query_files(session_cookie, " ".join(keywords), extensions)
    if not files:
        print("No results found.")
        return

    semaphore = asyncio.Semaphore(5)  # Limit concurrent downloads to 5
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(file_info, session, pdf_keywords, semaphore) for file_info in files]
        for result in await asyncio.gather(*tasks):
            if result:
                results.append(result)

    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(results, outfile, indent=4)
    print(f"Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main function
