import os
import base64
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils import (
    pdf_add_outline_item,
    prepare_chrome_driver,
    save_data,
    visit_page,
    merge_pdfs,
    make_page_pdf
)

ARTICLES_URL = 'https://lilianweng.github.io/posts/'

def posts_pagination_next_href(driver):
    try:
        next_href = driver \
            .find_element(By.CSS_SELECTOR, 'a.next') \
            .get_attribute('href')
        return next_href
    except NoSuchElementException:
        return

def posts_pagination_list_links(driver):
    elements = driver.find_elements(By.CSS_SELECTOR, 'a.entry-link')
    return [el.get_attribute('href') for el in elements]

def get_article_links(driver):
    visit_page(driver, ARTICLES_URL)
    links = []

    links.extend(posts_pagination_list_links(driver))
    while next_href := posts_pagination_next_href(driver):
        visit_page(driver, next_href)
        links.extend(posts_pagination_list_links(driver))

    return links

def prepare_article_page(driver):
    script = """
        ['header', 'footer', 'toc', 'post-footer', 'top-link'].forEach(className => {
            let elements = document.getElementsByClassName(className);
            for (let el of elements) {
                el.remove()
            }
        });
    """
    driver.execute_script(script)

def get_article_title(driver) -> str:
    title_locator = (By.CSS_SELECTOR, 'h1.post-title')
    title_element = driver.find_element(*title_locator)
    return title_element.text

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
    merged_pdf = merge_pdfs(pdfs)
    filename = './out/lillog.pdf'
    save_data(merged_pdf, filename)
    print(f'Saved to {filename}')

if __name__ == '__main__':
    main()
