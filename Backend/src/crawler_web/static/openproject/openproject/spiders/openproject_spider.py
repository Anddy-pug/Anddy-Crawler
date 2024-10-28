import scrapy
from scrapy.http import FormRequest
from urllib.parse import urlparse
from openproject.items import WebContentItem

class OpenprojectSpiderSpider(scrapy.Spider):
    name = "openproject_spider"
    allowed_domains = ["192.168.140.254"]
    start_urls = ["https://192.168.140.254:33005/login"]

    def start_requests(self):
        login_url = 'https://192.168.140.254:33005/login'
        yield scrapy.Request(login_url, callback=self.login)
    
    def login(self, response):
        token_value = response.css("form input[name=authenticity_token]::attr(value)").extract_first()
        utf_value = response.css("form input[name=utf8]::attr(value)").extract_first()
        return FormRequest.from_response(response,
                                         formdata={'utf8': utf_value, 
                                                   'authenticity_token': token_value,
                                                   'password': 'pug0620',
                                                   'username': 'pug0620',
                                                   'login': 'Sign in'},
                                         callback=self.parse)

    def parse(self, response):
        # Extract text from h1, h2, h3, and p tags
        item = WebContentItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get(default='No title found')
        item['p'] = response.css('p::text').getall()
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
        # Check if the hostname is allowed and the path contains the target folder
        return (
            parsed_url.hostname in self.allowed_domains and 
            "/projects/" in parsed_url.path
        )
