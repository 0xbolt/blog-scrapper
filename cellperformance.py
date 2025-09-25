import os
import base64
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from pypdf import PdfWriter, PdfReader

from utils import merge_pdfs

BASE_URL = 'https://cellperformance.beyond3d.com'

def prepare_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    return driver

def visit_page(driver, link):
    driver.get(link)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

def get_article_links(driver):
    articles_div_locator = (By.CSS_SELECTOR, 'div.widget-recent-entries.widget-archives.widget')
    articles_div = driver.find_element(*articles_div_locator)
    article_links = [el.get_attribute('href') for el in articles_div.find_elements(By.CSS_SELECTOR, 'li a[href]')]

    return article_links

def clean_article_page(driver):
    # entry_div_locator = (By.CSS_SELECTOR, 'div.entry-asset.asset.hentry')
    # entry_div = driver.find_element(*entry_div_locator)

    # delete extraneous content, set article to page width
    script = """
        // delete extraneous content
        ['header','footer','beta'].forEach(id => {
            let el = document.getElementById(id);
            if (el) el.remove();
        });

        // set article to page width
        ['content-inner','alpha'].forEach(id => {
            let el = document.getElementById(id);
            if (el) el.style.width = '100%';
        });
    """
    driver.execute_script(script)

def get_article_title(driver) -> str:
    entry_title_div_locator = (By.CSS_SELECTOR, 'h1.asset-name.entry-title')
    entry_title_div = driver.find_element(*entry_title_div_locator)
    return entry_title_div.text

def get_article_page_pdf(driver) -> bytes:
    # A5 Paper
    PDF_OPTIONS = {
        "printBackground": True,
        "paperWidth": 5.83,
        "paperHeight": 8.27,
        "marginTop": 0.4,
        "marginBottom": 0.4,
        "marginLeft": 0.4,
        "marginRight": 0.4
    }
    pdf = driver.execute_cdp_cmd("Page.printToPDF", PDF_OPTIONS)
    pdf_bytes = base64.b64decode(pdf['data'])

    def add_article_outline(input_pdf: bytes) -> bytes:
        writer = PdfWriter()
        title = get_article_title(driver)

        writer.append(PdfReader(BytesIO(input_pdf)))
        writer.add_outline_item(title, 0)

        output_pdf_buffer = BytesIO()
        writer.write(output_pdf_buffer)
        output_pdf_buffer.seek(0)
        output_pdf = output_pdf_buffer.read()

        return output_pdf

    pdf_bytes = add_article_outline(pdf_bytes)
    return pdf_bytes

def main():
    driver = prepare_driver()
    visit_page(driver, BASE_URL)
    article_links = get_article_links(driver)
    print(f'Found {len(article_links)} article links')

    pdfs = []
    for link in article_links:
        visit_page(driver, link)
        clean_article_page(driver)
        pdfs.append(get_article_page_pdf(driver))
        print(f'Fetched article: {get_article_title(driver)}')

    merged = merge_pdfs(pdfs)
    path = './out/cellperformance.pdf'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(merged)
    print(f'Saved to {path}')

if __name__ == '__main__':
    main()
