import requests
import io
from pdf2image import convert_from_bytes
import pytesseract
from urllib.parse import quote
from multiprocessing import Process, Queue

def download_pdf(url):
    """
    Download a PDF from the given URL with a timeout and return its content as a BytesIO object.
    """
    try:
        response = requests.get(url, timeout=10)  # 10-second timeout for downloading
        if response.status_code == 200 and "application/pdf" in response.headers.get("Content-Type", ""):
            return io.BytesIO(response.content)
        else:
            print(f"Failed to download PDF: {url} with status code {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        print(f"Timeout while downloading PDF: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error while downloading PDF: {url}, Error: {e}")
        return None



def ocr_worker(pdf_bytes, queue):
    """
    Worker function for OCR to be run in a separate process.
    """
    try:
        images = convert_from_bytes(pdf_bytes)
        full_text = ""
        for image in images:
            full_text += pytesseract.image_to_string(image, lang='eng', config='--psm 6')
        queue.put(full_text)  # Send the result back via the queue
    except Exception as e:
        queue.put(f"OCR error: {e}")

def extract_text_with_tesseract(pdf_file, timeout=30):
    """
    Extract text using Tesseract OCR with a timeout enforced via multiprocessing.
    """
    queue = Queue()
    process = Process(target=ocr_worker, args=(pdf_file.getvalue(), queue))
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

def analyze_pdf_content(text, keywords):
    """
    Analyze text content for keyword occurrences.
    """
    keyword_counts = {keyword: text.lower().count(keyword.lower()) for keyword in keywords}
    return keyword_counts

