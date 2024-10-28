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
    """Custom exception for crawler configuration errors."""
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
        """
        Initialize the WebCrawler with configuration parameters.

        :param elasticsearch_url: URL of the Elasticsearch instance.
        :param elasticsearch_username: Username for Elasticsearch.
        :param elasticsearch_password: Password for Elasticsearch.
        :param index_name: Elasticsearch index name.
        :param login_url: URL of the target site's login page.
        :param target_username: Username for the target site.
        :param target_password: Password for the target site.
        :param username_field_id: HTML ID of the username input field.
        :param password_field_id: HTML ID of the password input field.
        :param submit_button_id: HTML ID of the login submit button.
        :param base_url: Base URL of the target site.
        """
        # Initialize Elasticsearch client

        # self.es = Elasticsearch(
        #     elasticsearch_url,
        #     ssl_assert_fingerprint=elasticsearch_fingerprint,
        #     basic_auth=(elasticsearch_username, elasticsearch_password)
        # )
        
        self.es = ElasticsearchConnector(elasticsearch_url, elasticsearch_username, elasticsearch_password, elasticsearch_fingerprint)
        
        # Check connection
        # if not self.es.ping():
        #     raise ConfigError("Cannot connect to Elasticsearch.")
        # self.index_name = index_name
        # # Create index if it doesn't exist
        # if not self.es.indices.exists(index=self.index_name):
        #     self.es.indices.create(index=self.index_name)
        #     logging.info(f"Created Elasticsearch index: {self.index_name}")

        # Selenium WebDriver setup with headless option for efficiency
        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # Run in headless mode
            # chrome_options.add_argument("--no-sandbox")
            # chrome_options.add_argument("--disable-dev-shm-usage")

            # chrome_options.add_argument("--headless")  # Run Chrome in headless mode (optional)
            # chrome_options.add_argument("--no-sandbox")  # Disable sandbox for Chrome
            # chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            # chrome_options.add_argument("--remote-debugging-port=9222")  # Specify a port for remote debugging
            # chrome_options.add_argument("--disable-gpu")  # Applicable for Windows, can help in some cases

            # chrome_options = Options()
            chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate warnings
            chrome_options.add_argument("--allow-insecure-localhost")

            profile_path = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data" 
            chrome_options.add_argument(f"user-data-dir={profile_path}")
            chrome_options.add_argument("profile-directory=Default")

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

        # chrome_options = Options()
        # chrome_options.add_argument("--user-data-dir=C:/Users/KKK/AppData/Local/Google/Chrome/User Data")  # Use your profile path
        # chrome_options.add_argument("profile-directory=Profile 18")  # Use the specific Chrome profile directory

        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # def login(self):    # testrail
    #     """Perform login to the target site."""
    #     try:
    #         self.driver.get(self.login_url)
    #         WebDriverWait(self.driver, 10).until(
    #             lambda x: x.execute_script("return document.readyState === 'complete'")
    #         )

    #         # Input username and password
    #         # self.driver.find_element(By.ID, "details-button").click()
    #         # self.driver.find_element(By.ID, "proceed-link").click()
    #         # WebDriverWait(self.driver, 10).until(
    #         #     lambda x: x.execute_script("return document.readyState === 'complete'")
    #         # )
    #         # username_input = WebDriverWait(self.driver, 10).until(
    #         #     EC.visibility_of_element_located((By.XPATH, "//input[@name='username']"))
    #         # )
    #         # username_input.send_keys(self.target_username)

    #         self.driver.find_element(By.ID, self.username_field_id).send_keys(self.target_username)
    #         self.driver.find_element(By.ID, self.password_field_id).send_keys(self.target_password)
    #         self.driver.find_element(By.ID, self.submit_button_id).click()

    #         # self.driver.find_element(By.CSS_SELECTOR, "input.button.-primary.button_no-margin").click()
    #         # self.driver.find_element(By.NAME, "login").click()

    #         # submit_button = WebDriverWait(self.driver, 10).until(
    #         #     EC.element_to_be_clickable((By.NAME, self.submit_button_id))
    #         # )

    #         # submit_button.click()


    #         # Wait for the main page to load after login
    #         WebDriverWait(self.driver, 10).until(
    #             lambda x: x.execute_script("return document.readyState === 'complete'")
    #         )
    #         logging.info("Successfully logged in to the target site.")
    #     except Exception as e:
    #         logging.error(f"Login failed: {e}")
    #         self.driver.quit()
    #         raise

    # def login(self):
    #     """Perform login to the target site."""
    #     try:
    #         self.driver.get('https://www.upwork.com/ab/account-security/login')
    #         WebDriverWait(self.driver, 30).until(
    #             lambda x: x.execute_script("return document.readyState === 'complete'")
    #         )
    #         time.sleep(15)

    #         # Check for the cookie consent modal and click the accept button
    #         try:
    #             cookie_accept_button = WebDriverWait(self.driver, 30).until(
    #                 EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
    #             )
    #             # Scroll into view and click the button
    #             self.driver.execute_script("arguments[0].scrollIntoView(true);", cookie_accept_button)
    #             cookie_accept_button.click()
    #             logging.info("Cookie consent accepted.")
    #         except Exception as e:
    #             logging.warning(f"Cookie consent button not found or not clickable: {e}")

    #         # Input username and password
    #         username_element = WebDriverWait(self.driver, 30).until(
    #             EC.visibility_of_element_located((By.ID, "login_username"))
    #         )
    #         self.driver.execute_script("arguments[0].scrollIntoView(true);", username_element)
    #         username_element.send_keys('legend_referee121@simplelogin.com')
    #         time.sleep(5)

    #         self.driver.find_element(By.ID, "login_password_continue").click()
    #         password_element = WebDriverWait(self.driver, 30).until(
    #             EC.visibility_of_element_located((By.ID, "login_password"))
    #         )
    #         password_element.send_keys(self.target_password)
    #         self.driver.find_element(By.ID, "login_control_continue").click()
    #         time.sleep(85)

    #         # Wait for the main page to load after login
    #         WebDriverWait(self.driver, 10).until(
    #             lambda x: x.execute_script("return document.readyState === 'complete'")
    #         )
    #         logging.info("Successfully logged in to the target site.")
    #     except Exception as e:
    #         logging.error(f"Login failed: {e}")
    #         self.driver.quit()
    #         raise


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
        # document = {
        #     'url': url,
        #     'title': title,
        #     'content': content,
        #     'thumbnail': favicon,
        #     'type': "web",
        #     'update': current_time,
        #     'embedding_content': "",
        #     'embedding_title': ""
        # }
        
        
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
        """
        Start the special crawling process for paginated URLs.
        """
        try:
            # self.login()

            for page in range(1, 100):
                paginated_url = f"https://www.upwork.com/nx/search/jobs?page={page}"
                logging.info(f"Crawling page {page}: {paginated_url}")
                # self.crawl_page(paginated_url)

                self.driver.get(paginated_url)
                WebDriverWait(self.driver, 10).until(
                    lambda x: x.execute_script("return document.readyState === 'complete'")
                )


            logging.info("Special crawling completed!")
        finally:
            self.driver.quit()


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




# crawler = WebCrawler_openproject(
#     elasticsearch_url="https://192.168.140.243:9200",
#     elasticsearch_username="elastic",
#     elasticsearch_password="welcome",
#     elasticsearch_fingerprint="4a9cddce08802c5d00cd798d46b7104212b43d2419763324e62a59b8b4ed8168",
#     index_name="openproject",
#     login_url="https://192.168.140.254:33005/login",
#     target_username="pug0620",
#     target_password="pug0620",
#     username_field_id="username",
#     password_field_id="password",
#     submit_button_id="login",
#     base_url="https://192.168.140.254:33005/projects",
#     not_url="logout"
# )




# crawler.start_crawling()


