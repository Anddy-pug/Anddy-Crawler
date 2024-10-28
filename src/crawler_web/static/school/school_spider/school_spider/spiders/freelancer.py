import scrapy
from urllib.parse import urlparse
from school_spider.items import FreelancerItem
import requests
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import random

class ReactSpiderSpider(scrapy.Spider):
    name = "freelancer_spider"
    allowed_domains = ["www.freelancer.com"]
    start_urls = ["https://www.freelancer.com/jobs"]
    max_pages = 100 
    
    # custom_settings = {
    #     'DOWNLOAD_DELAY': random.uniform(2, 5),  # Random delay between 2 and 5 seconds
    #     'RETRY_ENABLED': True,
    #     'RETRY_TIMES': 5,  # Retry up to 5 times
    #     'RETRY_HTTP_CODES': [429, 500, 502, 503, 504],
    # }

    def clean_html(self, raw_html):
        # Use the `lxml` library to remove HTML tags
        from lxml import html
        clean_text = html.fromstring(raw_html).text_content()
        return clean_text.strip()
    
    def __init__(self, myconfig=None, *args, **kwargs):
        super(ReactSpiderSpider, self).__init__(*args, **kwargs)
        self.page_number = 1  # Start at page 1
        # print('+++++++++++++++++++++:' + str(myconfig))
        # self.myconfig = myconfig  # Store it as an instance attribute
        # crawler_setting = get_crawler_setting(myconfig, "web")
        # # adsf = start_urls
        # self.start_urls = [crawler_setting['url']]
        # self.allowed_domains = [extract_ip_or_default(crawler_setting['url'])]

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

    def get_page_content(self, url):
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Use Scrapy's Selector to create a response-like object
            selector = Selector(text=response.text)
            
            return selector
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def parse(self, response):
        # response = self.get_page_content(url)
        # text = self.clean_html(str(response))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # file_name = 'response_text.txt'
        # with open(file_name, 'w', encoding='utf-8') as file:
        #     file.write(text)
        # self.parse_page('https://www.freelancer.com/projects/japanese-translator/local-tokyo-car-dealership-translator')
        # Loop through each job item
        for job_item in response.css('div.JobSearchCard-item-inner'):
            # Extract the URL from the anchor tag
            job_url = job_item.css('a.JobSearchCard-primary-heading-link::attr(href)').get()
            if job_url:
                # Form the full URL (assuming the site uses relative URLs)
                full_url = response.urljoin(job_url)
                print(full_url)
                yield scrapy.Request(url=full_url, callback=self.parse_page)

        # Optionally, handle pagination to get more items if the site has multiple pages
        if self.page_number < self.max_pages:
            self.page_number += 1
            next_page_url = f"https://www.freelancer.com/jobs/{self.page_number}"  # Increment page number in URL
            print(f'@@@@@@@@@Next Page URL: {next_page_url}')
            yield response.follow(next_page_url, self.parse)
        else:
            print('@@@@@@@@@ No more pages to crawl')

    def parse_page(self, response):
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        item = FreelancerItem()
        # response = self.get_page_content(url)
        # # text = self.clean_html(str(response))
        # text = str(response)
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # file_name = 'response_text.txt'
        # with open(file_name, 'w', encoding='utf-8') as file:
        #     file.write(text)
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        
        # Extracting the title
        title = response.xpath('//h1[@data-size="large"]/text()').get()

        # Extracting the content
        description_blocks = response.xpath('//fl-text[contains(@class, "Project-description")]//div[@role="paragraph"]//text()').getall()

        # Clean and join relevant text content
        clean_text = ' '.join([text.strip() for text in description_blocks if text.strip()]).strip()


        # Extracting fields (skills/tags)
        fields = response.xpath('//fl-tag//div[@class="Content ng-star-inserted"]/text()').getall()
        fields = ', '.join(fields).strip()

        # Extracting country
        # country = response.xpath('//div[@class="NativeElement"]/text()').get().strip()
        # country = response.xpath('//fl-text//div[@role="paragraph" and contains(@data-size, "xsmall")]/text()').get()
        location = response.xpath("//div[contains(@class, 'IconContainer')]/following-sibling::fl-text//div[@role='paragraph']/text()").get()
        
        # Strip whitespace from the extracted text
        location = location.strip() if location else None
        # county = tree.xpath("//fl-text/div[contains(@class, 'NativeElement') and contains(text(), ',')]/text()[1]")

        price = response.xpath('//h2[contains(@class, "ng-star-inserted")]/text()').get()

        
        # Extracting rank (rating)
        rating = response.xpath('//fl-bit[contains(@class, "ValueBlock")]/text()').get()
        
        review_count = response.xpath('//fl-review-count//div[@role="paragraph"]/text()').get()
        
        # Extract payment verification status
        payment_verification = response.xpath('//div[contains(text(), "Payment method verified")]/text()').get()
        
        # Extract membership date
        member_since = response.xpath('//div[contains(text(), "Member since")]/text()').get()

        bid = response.xpath("//div[@role='paragraph' and @class='NativeElement']/text()").get()
        
        item['title'] = str(title)
        item['content'] = str(clean_text)
        item['fields'] = str(fields)
        item['location'] = str(location)
        item['price'] = str(price)
        item['rating'] = str(rating)
        item['review_count'] = str(review_count)
        item['payment_verification'] = str(payment_verification)
        item['member_since'] = str(member_since)
        item['bid'] = str(bid)
        
        
        
        print('Title::: ' + str(title))        
        print('Content::: ' + str(clean_text))        
        print('Fields::: ' + str(fields))        
        print('Country::: ' + str(location))        
        print('Price::: ' + str(price))   
        print('Rating::: ' + str(rating))  
        print('Review::: ' + str(review_count))        
        print('Payment::: ' + str(payment_verification))   
        print('Member::: ' + str(member_since))
        print('Bid::: ' + str(bid))

        yield item

        # Output the extracted data
        # yield {
        #     'title': title,
        #     'content': content,
        #     'fields': fields,
        #     'country': country,
        #     'rank': rank
        # }

    # def parse(self, response):
    #     # Extract text from h1, h2, h3, and p tags
    #     item = WebContentItem()
    #     item['url'] = response.url
    #     item['title'] = response.css('title::text').get(default='No title found')
    #     content = ' '.join(response.css('p::text').getall())
    #     cleaned_content = content.replace('\n', ' ').replace("'", "").strip()
    #     item['content'] = ' '.join(cleaned_content.split())
    #     print("~~~~~~~~~~~~~~~" + item['content'])
    #     # item['links'] = response.css('a::attr(href)').getall()
    #     item['favicon'] = self.extract_favicon(response)

    #     yield item

    #     # Extract all links from the page
    #     links = response.css('a::attr(href)').getall()

    #     for link in links:
    #         if link.startswith('/'):  # Handle relative URLs
    #             link = response.urljoin(link)
    #         elif not link.startswith('http'):
    #             # Handle other relative URLs (e.g., relative to current path)
    #             link = response.urljoin(link)

    #         # Ensure the link is within the allowed domains and specific path
    #         if self.is_allowed(link):
    #             yield scrapy.Request(link, callback=self.parse)

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
            "www.freelancer.com" in parsed_url.path
        )
