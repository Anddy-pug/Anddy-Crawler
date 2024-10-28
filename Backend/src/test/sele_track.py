import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, base_url, download_dir='downloaded_site'):
        self.base_url = base_url
        self.download_dir = download_dir
        self.visited_urls = set()

        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless
        service = Service(executable_path=r'G:\driver\129.0.6668.89\chromedriver-win32\chromedriver.exe')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Initialize WebDriverWait with a timeout of 10 seconds
        wait = WebDriverWait(self.driver, 10)
        # Create a directory to save downloaded content
        os.makedirs(self.download_dir, exist_ok=True)

    def crawl(self, url):
        if url in self.visited_urls:
            return
        self.visited_urls.add(url)
        
        print(f'Crawling: {url}')
        self.driver.get(url)
        
        # Wait until the page is fully loaded
        WebDriverWait(self.driver, 10).until(
            lambda x: x.execute_script("return document.readyState === 'complete'")
        )

        # Extract HTML content
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.save_html(url, soup)

        # Extract and download assets
        self.download_assets(soup)

        # Find and crawl all links on the page
        for link in soup.find_all('a', href=True):
            full_link = urljoin(url, link['href'])
            if self.is_valid_url(full_link):
                self.crawl(full_link)

    def save_html(self, url, soup):
        # Define a path to save HTML file
        path = self.get_file_path(url, 'html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))

    def download_assets(self, soup):
        for img in soup.find_all('img', src=True):
            asset_url = urljoin(self.base_url, img['src'])
            self.download_file(asset_url)

        for link in soup.find_all('link', href=True):
            asset_url = urljoin(self.base_url, link['href'])
            self.download_file(asset_url)

        for script in soup.find_all('script', src=True):
            asset_url = urljoin(self.base_url, script['src'])
            self.download_file(asset_url)

    def download_file(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Define path to save the asset
            path = self.get_file_path(url)
            with open(path, 'wb') as f:
                f.write(response.content)
                print(f'Downloaded: {path}')
        except Exception as e:
            print(f'Failed to download {url}: {e}')

    def get_file_path(self, url, ext=''):
        # Parse URL to create a file path
        parsed_url = urlparse(url)
        path = os.path.join(self.download_dir, parsed_url.netloc, parsed_url.path.lstrip('/'))
        
        if ext:
            path = os.path.splitext(path)[0] + '.' + ext
        
        os.makedirs(os.path.dirname(path), exist_ok=True)  # Create directories if needed
        return path

    def is_valid_url(self, url):
        # Check if the URL is within the same domain
        return urlparse(url).netloc == urlparse(self.base_url).netloc

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    base_url = 'https://www.elastic.co/'  # Replace with your target URL
    scraper = WebScraper(base_url)
    scraper.crawl(base_url)
    scraper.close()
