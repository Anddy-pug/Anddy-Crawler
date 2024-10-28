import scrapy
from urllib.parse import urlparse
from school_spider.items import WebContentItem
import sys
import os
from urllib.parse import urlparse
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../../../../../..'))
sys.path.append(parent_dir)
from embedding.embedding import *
from search_engine.elasticsearch_connector import *
from parser.text_parser import *

class ReactSpiderSpider(scrapy.Spider):
    name = "react_spider"
    # allowed_domains = ["192.168.140.238"]
    # start_urls = ["http://192.168.140.238/w3school/www.w3schools.com/react"]

    def __init__(self, myconfig=None, *args, **kwargs):
        super(ReactSpiderSpider, self).__init__(*args, **kwargs)
        print('+++++++++++++++++++++:' + str(myconfig))
        self.myconfig = myconfig  # Store it as an instance attribute
        crawler_setting = get_crawler_setting(myconfig, "web")
        # adsf = start_urls
        self.start_urls = [crawler_setting['url']]
        self.allowed_domains = [extract_ip_or_default(crawler_setting['url'])]

    def parse(self, response):
        
        main_content = response.css('#main')

        # Extract all <p> tags within the main content
        p_tags = main_content.css('p::text').getall()
        
        # Extract text from h1, h2, h3, and p tags
        item = WebContentItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get(default='No title found')
        content = ' '.join(p_tags)
        cleaned_content = content.replace('\n', ' ').replace("'", "").strip()
        item['content'] = ' '.join(cleaned_content.split())
        print("~~~~~~~~~~~~~~~" + item['content'])
        # item['links'] = response.css('a::attr(href)').getall()
        item['favicon'] = self.extract_favicon(response)

        yield item

        # Extract all links from the page
        links = response.css('a::attr(href)').getall()

        for link in links:
            if link.startswith('/'):  # Handle relative URLs
                link = response.urljoin(link)
            elif not link.startswith('http'):
                # Handle other relative URLs (e.g., relative to current path)
                link = response.urljoin(link)

            # Ensure the link is within the allowed domains and specific path
            if self.is_allowed(link):
                yield scrapy.Request(link, callback=self.parse)

    def extract_favicon(self, response):
        # Find the favicon link
        favicon = response.css('link[rel="icon"]::attr(href)').get()
        if not favicon:
            favicon = response.css('link[rel="shortcut icon"]::attr(href)').get()
        if favicon:
            # Convert relative URLs to absolute URLs
            return response.urljoin(favicon)
        return None

    def is_allowed(self, url):
        parsed_url = urlparse(url)
        # print("@@@@@@@@@@@@" + parsed_url.hostname)
        # print("@@@@@@@@@@@@" + parsed_url.path)
        # print("@@@@@@@@@@@@" + parsed_url.hostname in self.allowed_domains and "/w3school/www.w3schools.com/react/" in parsed_url.path)
        # Check if the hostname is allowed and the path contains the target folder
        return (
            parsed_url.hostname in self.allowed_domains and 
            urlparse(url).path in parsed_url.path
        )
