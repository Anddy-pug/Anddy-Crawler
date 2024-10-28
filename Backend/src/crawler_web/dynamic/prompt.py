# src/crawler/web_crawler.py

import re
import logging
from urllib.parse import urlparse
from threading import Thread, Lock
from typing import List
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from elasticsearch import Elasticsearch, NotFoundError
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support import expected_conditions as EC
from scrapy import Selector
import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse, urljoin
import colorama 
import sys
import time
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../..'))
sys.path.append(parent_dir)
from embedding.embedding import *
from search_engine.elasticsearch_connector import *
from parser.text_parser import *

colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ConfigError(Exception):
    pass


class WebCrawler_openproject:
    def __init__(
        self,
        elasticsearch_url: str,
        elasticsearch_username: str,
        elasticsearch_password: str,
        elasticsearch_fingerprint: str,
        index_name: str,
        login_url: str,
        target_username: str,
        target_password: str,
        username_field_id: str,
        password_field_id: str,
        submit_button_id: str,
        base_url: str,
        not_url: str
    ):

        
        self.es = ElasticsearchConnector(elasticsearch_url, elasticsearch_username, elasticsearch_password, elasticsearch_fingerprint)
        

        try:
            chrome_options = Options()

            chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate warnings
            chrome_options.add_argument("--allow-insecure-localhost")

            # profile_path = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data" 
            # chrome_options.add_argument(f"user-data-dir={profile_path}")
            # chrome_options.add_argument("profile-directory=Default")

            # self.driver = driver = webdriver.Chrome(service=Service(os.path.dirname(__file__) + '/chromedriver.exe'), options=chrome_options)
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

            # self.driver = driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            self.driver.set_page_load_timeout(30)
        except Exception as e:
            raise ConfigError(f"Selenium WebDriver initialization error: {e}")

        # Credentials and selectors
        self.login_url = login_url
        self.elasticsearch_fingerprint = elasticsearch_fingerprint
        self.target_username = target_username
        self.target_password = target_password
        self.username_field_id = username_field_id
        self.password_field_id = password_field_id
        self.submit_button_id = submit_button_id
        self.base_url = base_url
        self.not_url = not_url

        # Visited URLs tracking
        self.visited_urls = set()
        self.visited_urls_lock = Lock()


    def login(self):
        """Let user manually solve CAPTCHA and try to bypass its reappearance."""
        try:
            # Load a real browser profile to avoid being detected by anti-bot measures

            # Navigate to the login page
            self.driver.get('https://www.upwork.com/ab/account-security/login')
            WebDriverWait(self.driver, 30).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )

            # Enter username and click Next
            username_element = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "login_username"))
            )
            username_element.send_keys(self.target_username)
            self.driver.find_element(By.ID, "login_password_continue").click()

            # Let the user manually solve the CAPTCHA
            logging.info("CAPTCHA page displayed. Please complete human verification manually.")
            print("CAPTCHA page displayed. Solve CAPTCHA manually.")

            # Wait for CAPTCHA to be solved (based on password field appearance)
            WebDriverWait(self.driver, 300).until(
                EC.visibility_of_element_located((By.ID, "login_password"))
            )

            # Continue login after CAPTCHA is solved
            password_element = WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "login_password"))
            )
            password_element.send_keys(self.target_password)
            self.driver.find_element(By.ID, "login_control_continue").click()

            # Wait for the main page to load after login
            WebDriverWait(self.driver, 30).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )

            logging.info("Successfully logged in to the target site.")
        except Exception as e:
            logging.error(f"Login failed: {e}")
            self.driver.quit()
            raise


    # def is_valid_url(self, url: str, base_domain: str) -> bool:
    #     """Check if a URL is valid and belongs to the base domain."""
    #     parsed_url = urlparse(url)
    #     return (
    #         parsed_url.scheme in ("http", "https") and
    #         base_domain in parsed_url.netloc and
    #         not url.endswith(self.not_url)
    #     )
    
        
    def is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid and belongs to the base domain, and contains 'work_packages'."""
        parsed_url = urlparse(url)
        return (
            parsed_url.scheme in ("http", "https") and
            'jobs' in parsed_url.path and  # Ensure the URL contains 'work_packages'
            not url.endswith(self.not_url)
    )

    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URLs by removing fragments."""
        return urlparse(url)._replace(fragment='').geturl()

    def send_to_elasticsearch(self, url: str, title: str, content: str, favicon: str):
        """Send crawled page data to Elasticsearch."""
        current_time = datetime.now()
        lang = detect_lang(content) 

        
        
        texts = custom_text_splitter(content, chunk_size=1500, chunk_overlap=200)
        embedding_title = get_text_embedding(title)
        for i, text in enumerate(texts):
            embedding_content = get_text_embedding(text)
            
            document = {
                'url': url,
                'title': title,
                'thumbnail': favicon,
                'content': text,
                'update': current_time,
                'type': "web",
                'embedding_content': embedding_content,
                'embedding_title': embedding_title,
                'chunk_id' : i,
                'lang' : lang
            }
        
        self.es.save_data(document, "product_web_openproject")


    def crawl_page(self, url: str) -> List[str]:
        """Crawl a single page and extract all valid URLs."""
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )

            if self.is_valid_url(url):
                time.sleep(1)
                page_title = self.driver.title

                # soup = BeautifulSoup(self.driver.find_element('tag name', 'body').get_attribute('innerText'), "html.parser")
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                content = soup.get_text()
                content = content.replace('\n', ' ').replace('\t', ' ')
                content = clean_text(content)
                print("@@@@@@@@@@@@" + content)
                favicon_url = self.extract_favicon(soup)

                # Save the HTML content of the page
                with self.visited_urls_lock:
                    self.send_to_elasticsearch(url, page_title, content, favicon_url)
                    self.visited_urls.add(url)

            # Find all links on the page
            links = self.driver.find_elements(By.TAG_NAME, "a")
            found_urls = [link.get_attribute('href') for link in links if link.get_attribute('href')]
            base_domain = urlparse(self.base_url).netloc
            # return [self.normalize_url(link) for link in found_urls if self.is_valid_url(link, base_domain)]
            return [self.normalize_url(link) for link in found_urls if self.is_valid_url(link)]
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            return []

    def extract_favicon(self, soup):
        """Extract the favicon URL from the BeautifulSoup object."""
        favicon = soup.find("link", rel=lambda x: x and 'icon' in x)
        if favicon and 'href' in favicon.attrs:
            return urljoin(self.driver.current_url, favicon['href'])  # Join with the current URL if relative
        return None


    def crawl_site(self, url: str):
        """Crawl the site recursively."""
        with self.visited_urls_lock:
            if url in self.visited_urls:
                return
            self.visited_urls.add(url)

        logging.info(f"Crawling: {url}")

        # Get found URLs from the current page
        found_urls = self.crawl_page(url)

        # Recursively crawl the found URLs
        for found_url in found_urls:
            try:
                self.crawl_site(found_url)
            except Exception as e:
                logging.error(f"Error while crawling {found_url}: {e}")

    def start_crawling(self):
        """Start the crawling process."""
        try:
            self.login()
            self.crawl_site(self.base_url)
            logging.info("Crawling completed!")
        finally:
            self.driver.quit()

    def start_special_crawling(self):

        self.driver.get("https://stablediffusionweb.com/prompts/user-interface")

        # Scroll down to the bottom of the page
        for _ in range(100):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
        html_content = self.driver.page_source
        
        response = Selector(text=html_content)
        
        urls = response.css('a.group.relative.block.cursor-pointer::attr(href)').getall()
        
        
        with open('extracted_urls.txt', 'w') as file:
            for url in urls:
                full_url = self.driver.current_url + url
                file.write(full_url + '\n')  # Write the full URL to the file


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='File crawler with argument input.')

    parser.add_argument('--crawler_name', type=str, default="nextcloud", help="")
    parser.add_argument('--crawler_type', type=str, default="web", help="")

    elastic_config = get_elasticsearch_setting()
    thumbnail_setting = get_thumbnail_setting()
    embedding_setting = get_embedding_setting()
    crawler_setting = get_crawler_setting(parser.parse_args().crawler_name, parser.parse_args().crawler_type)

    crawler = WebCrawler_openproject(
        elasticsearch_url=elastic_config['elasticsearch_url'],
        elasticsearch_username=elastic_config['elasticsearch_username'],
        elasticsearch_password=elastic_config['elasticsearch_password'],
        elasticsearch_fingerprint=elastic_config['elasticsearch_fingerprint'],
        index_name='upwork_jobs',
        login_url=crawler_setting['login_url'],
        target_username=crawler_setting['username'],
        target_password=crawler_setting['password'],
        username_field_id="username",
        password_field_id="password",
        submit_button_id="login",
        base_url=crawler_setting['url'],
        not_url="logout"
    )

    # crawler.start_crawling()
    crawler.start_special_crawling()


