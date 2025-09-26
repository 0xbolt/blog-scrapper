import os
import base64
from io import BytesIO
from pypdf import PdfReader, PdfWriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from pypdf import PdfWriter, PdfReader

def prepare_chrome_driver(dev: bool = False) -> webdriver.Chrome:
    options = Options()
    if not dev:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver

def visit_page(driver: webdriver.Chrome, link):
    driver.get(link)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def merge_pdfs(pdfs: list[bytes]) -> bytes:
    buffer = BytesIO()
    writer = PdfWriter()
    for pdf_bytes in pdfs:
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_reader = PdfReader(pdf_buffer)
        writer.append(pdf_reader)
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()

def pdf_add_outline_item(pdf: bytes, title, page_number=0) -> bytes:
    writer = PdfWriter()
    writer.append(PdfReader(BytesIO(pdf)))
    writer.add_outline_item(title, 0)

    buffer = BytesIO()
    writer.write(buffer)
    buffer.seek(0)
    return buffer.read()

def make_page_pdf(driver: webdriver.Chrome) -> bytes:
    # A5 Paper
    PDF_OPTIONS = {
        "printBackground": False,
        "paperWidth": 5.83,
        "paperHeight": 8.27,
        "marginTop": 0.4,
        "marginBottom": 0.4,
        "marginLeft": 0.4,
        "marginRight": 0.4,
    }
    result = driver.execute_cdp_cmd("Page.printToPDF", PDF_OPTIONS)
    pdf = base64.b64decode(result['data'])
    return pdf

def save_data(data: bytes, filename: str):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        f.write(data)