import os
from selenium.webdriver.common.by import By

from utils import (
    make_page_pdf,
    pdf_add_outline_item,
    prepare_chrome_driver,
    visit_page,
    merge_pdfs,
)

ARTICLES_URL = 'https://cellperformance.beyond3d.com/articles/'

def get_article_links(driver):
    articles_div_locator = (By.CSS_SELECTOR, 'div.widget-recent-entries.widget-archives.widget')
    articles_div = driver.find_element(*articles_div_locator)
    article_links = [el.get_attribute('href') for el in articles_div.find_elements(By.CSS_SELECTOR, 'li a[href]')]

    return article_links

def prepare_article_page(driver):
    script = """
        ['header','footer','beta'].forEach(id => {
            let el = document.getElementById(id);
            if (el) el.remove();
        });

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

def make_article_page_pdf(driver) -> bytes:
    pdf = make_page_pdf(driver)
    title = get_article_title(driver)
    outlined_pdf = pdf_add_outline_item(pdf, title)
    return outlined_pdf

def main():
    driver = prepare_chrome_driver()

    # Get all article links
    visit_page(driver, ARTICLES_URL)
    article_links = get_article_links(driver)
    print(f'Found {len(article_links)} article links')

    pdfs = []
    # Fetch each article and output a PDF
    for link in article_links:
        visit_page(driver, link)
        prepare_article_page(driver)
        pdfs.append(make_article_page_pdf(driver))
        print(f'Fetched article: {get_article_title(driver)}')

    # Merge article into a single PDF and save
    merged = merge_pdfs(pdfs)
    path = './out/cellperformance.pdf'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(merged)
    print(f'Saved to {path}')

if __name__ == '__main__':
    main()
