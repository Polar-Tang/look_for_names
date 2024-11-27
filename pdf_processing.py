import requests
import io
from pdf2image import convert_from_bytes
import pytesseract
from urllib.parse import quote
from multiprocessing import Process, Queue
import asyncio
import aiohttp

async def download_pdf_async(url, session):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                print(f"Failed to download {url}: {response.status}")
                return None
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return None


def ocr_worker(pdf_bytes, queue):
    """
    Worker function for OCR to be run in a separate process.
    """
    try:
        images = convert_from_bytes(pdf_bytes)
        full_text = ""
        for image in images:
            full_text += pytesseract.image_to_string(image, lang='eng', config='--psm 3')
        queue.put(full_text)  # Send the result back via the queue
    except Exception as e:
        queue.put(f"OCR error: {e}")

def extract_text_with_tesseract(pdf_bytes, timeout=30):
    """
    Extract text using Tesseract OCR with a timeout enforced via multiprocessing.
    """
    queue = Queue()
    process = Process(target=ocr_worker, args=(pdf_bytes, queue))
    process.start()
    process.join(timeout)

    if process.is_alive():
        print(f"Tesseract OCR timed out after {timeout} seconds.")
        process.terminate()  # Forcefully terminate the process
        process.join()  # Ensure cleanup
        return None

    # Retrieve the result from the queue
    if not queue.empty():
        return queue.get()
    return None

async def process_pdf(url, pdf_keywords):
    """
    Download and analyze a PDF asynchronously.
    """
    print(f"Starting download for: {url}")
    pdf_data = await download_pdf_async(url)
    if not pdf_data:
        print(f"Skipping {url} due to download failure.")
        return None

    print(f"Running OCR for: {url}")
    text = extract_text_with_tesseract(pdf_data)
    if not text:
        print(f"Skipping {url} due to OCR failure.")
        return None

    print(f"Analyzing content for: {url}")
    return analyze_pdf_content(text, pdf_keywords)

def analyze_pdf_content(text, pdf_keywords):
    """
    Analyze the extracted text for specific keywords.
    """
    keyword_counts = {keyword: text.lower().count(keyword.lower()) for keyword in pdf_keywords}
    return keyword_counts
