import scrapy
from urllib.parse import urlparse
from school_spider.items import FreelancerItem
import requests
from scrapy.selector import Selector
from bs4 import BeautifulSoup
import random
import urllib.request
import os
import pandas as pd



class ReactSpiderSpider(scrapy.Spider):
    name = "prompt_spider"
    allowed_domains = ["stablediffusionweb.com"]
    start_urls = ["https://stablediffusionweb.com/prompts/ui-design"]
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

    # def start_requests(self):
    #     login_url = 'https://192.168.140.254:33005/login'
    #     yield scrapy.Request(login_url, callback=self.login)
    
    # def login(self, response):
    #     token_value = response.css("form input[name=authenticity_token]::attr(value)").extract_first()
    #     utf_value = response.css("form input[name=utf8]::attr(value)").extract_first()
    #     return FormRequest.from_response(response,
    #                                      formdata={'utf8': utf_value, 
    #                                                'authenticity_token': token_value,
    #                                                'password': 'pug0620',
    #                                                'username': 'pug0620',
    #                                                'login': 'Sign in'},
    #                                      callback=self.parse)

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
        
        filename = 'extracted_urls.txt'
        urls = self.read_urls_from_file(filename)

        # for link in response.css('a.group.relative.block.cursor-pointer'):
        for url in urls:
            
            # url = link.css('::attr(href)').get()
            # if url:
            #     full_url = response.urljoin(url)
            #     print(full_url)
                # yield scrapy.Request(url=full_url, callback=self.parse_page)
                
            yield scrapy.Request(url=url, callback=self.parse_page)
            print(url)


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
        title = response.css('h1.text-2xl.font-bold.text-gray-900::text').get()

        # Extracting the content
        clean_text = response.css('a.cursor-pointer.rounded.bg-opacity-0.transition-all.duration-200.hover\\:bg-opacity-40.hover\\:text-white.bg-red-500::text').get()

        # Clean and join relevant text content
        # clean_text = ' '.join([text.strip() for text in description_blocks if text.strip()]).strip()


        # Extracting fields (skills/tags)
        fields = response.xpath('//fl-tag//div[@class="Content ng-star-inserted"]/text()').getall()
        fields = ', '.join(fields).strip()
        
        
        location = response.css('dd.text-sm.leading-6.text-gray-500::text').get()
        
        # Strip whitespace from the extracted text
        location = location.strip() if location else None
        # county = tree.xpath("//fl-text/div[contains(@class, 'NativeElement') and contains(text(), ',')]/text()[1]")

        price = response.css('dd.text-sm.leading-6.text-gray-500::text').get()

        extracted_values = []
        # Extracting rank (rating)
        dimension = response.xpath('//dd[@class="text-sm leading-6 text-gray-500"]')
        for value in dimension:
            text = ''.join(value.xpath('./text()').getall()).strip()
            if text:  # Only add non-empty texts
                extracted_values.append(text)
        
        image_url = response.css('img.w-full::attr(src)').get()
        # item['title'] = str(title)
        # item['content'] = str(clean_text)
        # item['fields'] = str(fields)
        # item['location'] = str(location)
        # item['price'] = str(price)
        # item['rating'] = str(rating)
        # item['review_count'] = str(review_count)
        # item['payment_verification'] = str(payment_verification)
        # item['member_since'] = str(member_since)
        # item['bid'] = str(bid)
        
        
        
        print('Title::: ' + str(title))        
        print('Content::: ' + str(clean_text))        
        print('Fields::: ' + str(fields))        
        print('Style::: ' + str(extracted_values[0]))        
        print('Aspect ratio::: ' + str(extracted_values[1]))   
        print('Size::: ' + str(extracted_values[2]))  
        print('URL::: ' + str(image_url))    

        self.download_file(image_url)
        
        
        data_entry = {
            'Title': title,
            'Content': clean_text,
            'Style': extracted_values[0] if len(extracted_values) > 0 else None,
            'Aspect Ratio': extracted_values[1] if len(extracted_values) > 1 else None,
            'Size': extracted_values[2] if len(extracted_values) > 2 else None,
            'URL': image_url,
            'FileName': os.path.basename(image_url),
        }
        
        # self.append_to_excel(data_entry)

        yield item

    def read_urls_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                urls = file.readlines()  # Read all lines from the file
                urls = [url.strip() for url in urls]  # Remove any leading/trailing whitespace
            return urls
        except FileNotFoundError:
            print(f"The file '{filename}' does not exist.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def append_to_excel(self, data_entry):
        excel_file_name = "extracted_data.xlsx"

        # Create a DataFrame from the new data entry
        new_df = pd.DataFrame([data_entry])

        # Check if the Excel file exists
        if os.path.exists(excel_file_name):
            # Load the existing data from the Excel file
            existing_df = pd.read_excel(excel_file_name)

            # Append new data to the existing DataFrame
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            # If the file does not exist, use the new DataFrame as the updated DataFrame
            updated_df = new_df

        # Save the updated DataFrame back to the Excel file
        with pd.ExcelWriter(excel_file_name, engine='openpyxl', mode='w') as writer:
            updated_df.to_excel(writer, index=False)

        print(f"Data appended to {excel_file_name}")


    def download_file(self, url):
        # Extract filename from the URL
        filename = os.path.basename(url)
        
        filename = "image/" + filename 
        
        try:
            urllib.request.urlretrieve(url, filename)
            print(f"File downloaded successfully: {filename}")
        except Exception as e:
            print(f"Failed to download file: {e}")



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
            "stablediffusionweb.com" in parsed_url.path
        )



# example

# <a hreflang="en" class="group relative block cursor-pointer overflow-hidden rounded-lg shadow-none transition-shadow ease-in-out hover:shadow-xl" href="/image/20704909-2048-chengdu-olympics-app-home-page"><img alt="2048 Chengdu Olympics App Home Page" loading="lazy" width="704" height="1408" decoding="async" data-nimg="1" class="block h-auto w-full bg-slate-200" src="https://imgcdn.stablediffusionweb.com/2024/10/22/7e854a9d-efb8-46cc-b3da-f4b5eece6b36.jpg" style="color: transparent; aspect-ratio: 704 / 1408;"><div class="absolute left-0 top-full flex h-full w-full items-end bg-gradient-to-b from-zinc-800/5 to-zinc-800/80 p-2 text-sm text-white transition-all group-hover:top-0"><p class="line-clamp-3 whitespace-pre-line break-words">2048 Chengdu Olympics App Home Page</p></div></a>


# <a hreflang="en" class="group relative block cursor-pointer overflow-hidden rounded-lg shadow-none transition-shadow ease-in-out hover:shadow-xl" href="/image/21046819-user-interface-icons-for-poolrooms-interaction"><img alt="User Interface Icons for Poolrooms Interaction" loading="lazy" width="1024" height="1024" decoding="async" data-nimg="1" class="block h-auto w-full bg-slate-200" style="color:transparent;aspect-ratio:1024/1024" src="https://imgcdn.stablediffusionweb.com/2024/10/27/ea3f4dcd-adee-49f9-8534-90af8d929e14.jpg"><div class="absolute left-0 top-full flex h-full w-full items-end bg-gradient-to-b from-zinc-800/5 to-zinc-800/80 p-2 text-sm text-white transition-all group-hover:top-0" bis_skin_checked="1"><p class="line-clamp-3 whitespace-pre-line break-words">User Interface Icons for Poolrooms Interaction</p></div></a>


# <h1 class="text-2xl font-bold text-gray-900">User Interface Game for Interaction</h1>


# <div class=" rounded-lg bg-gray-50 py-6 shadow-sm ring-1 ring-gray-900/5" bis_skin_checked="1"><div class="flex-auto pl-6" bis_skin_checked="1"><h2 class="text-lg font-medium text-gray-900">AI Art Image Prompt</h2></div><div class="max-h-[72.5vh] overflow-auto" bis_skin_checked="1"><div class="mt-6 flex w-full flex-none flex-col gap-x-4 border-t border-gray-900/5 px-6 pt-6" bis_skin_checked="1"><span class="mb-1 w-full">Prompt:</span><div class="overflow-auto bg-white p-4 shadow sm:rounded-lg" style="max-height: 15.125rem;" bis_skin_checked="1"><div class="break-words" bis_skin_checked="1"><span><a hreflang="en" class="cursor-pointer rounded bg-opacity-0 transition-all duration-200 hover:bg-opacity-40 hover:text-white bg-red-500" href="/prompts/user-interface">user interface </a>, </span><span><a hreflang="en" class="cursor-pointer rounded bg-opacity-0 transition-all duration-200 hover:bg-opacity-40 hover:text-white bg-orange-500" href="/prompts/game">  game </a>, </span><span><a hreflang="en" class="cursor-pointer rounded bg-opacity-0 transition-all duration-200 hover:bg-opacity-40 hover:text-white bg-yellow-500" href="/prompts/for-interaction"> for interaction</a></span></div><div class="mt-2 flex flex-wrap items-center gap-2 whitespace-nowrap" bis_skin_checked="1"><div class="flex flex-1 items-center gap-2" bis_skin_checked="1"><button class="items-center justify-center font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground h-8 text-sm flex flex-1 rounded-sm px-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy mr-2 h-4 w-4"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>Copy Prompt</button><button class="items-center justify-center font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground h-8 text-sm flex flex-1 rounded-sm px-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-link mr-2 h-4 w-4"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>Copy URL</button></div><button class="items-center justify-center font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground h-8 text-sm flex shrink-0 rounded-sm px-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link h-4 w-4"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" x2="21" y1="14" y2="3"></line></svg></button></div></div></div><div class="mt-6 flex w-full flex-none flex-col gap-x-4 border-t border-gray-900/5 px-6 pt-6" bis_skin_checked="1"><span class="mb-1 w-full">Negative prompt:</span><div class="overflow-auto bg-white p-4 shadow sm:rounded-lg" style="max-height: 15.125rem;" bis_skin_checked="1"><div class="break-words" bis_skin_checked="1"><span class="cursor-pointer rounded bg-opacity-0 transition-all duration-200 hover:bg-opacity-40">, </span></div><div class="mt-2 flex flex-wrap items-center gap-2 whitespace-nowrap" bis_skin_checked="1"><div class="flex flex-1 items-center gap-2" bis_skin_checked="1"><button class="items-center justify-center font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground h-8 text-sm flex flex-1 rounded-sm px-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy mr-2 h-4 w-4"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>Copy Prompt</button></div><button class="items-center justify-center font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground h-8 text-sm flex shrink-0 rounded-sm px-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-external-link h-4 w-4"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" x2="21" y1="14" y2="3"></line></svg></button></div></div></div><div class="mt-4 flex w-full flex-none gap-x-4 px-6" bis_skin_checked="1"><dt class="flex-none"><span>Style:</span></dt><dd class="text-sm leading-6 text-gray-500">Futurism</dd></div><div class="mt-4 flex w-full flex-none gap-x-4 px-6" bis_skin_checked="1"><dt class="flex-none"><span>Aspect ratio:</span></dt><dd class="text-sm leading-6 text-gray-500">1:1</dd></div><div class="mt-4 flex w-full flex-none gap-x-4 px-6" bis_skin_checked="1"><dt class="flex-none"><span>Size:</span></dt><dd class="text-sm leading-6 text-gray-500">1024 X 1024</dd></div><div class="mt-6 flex w-full border-t border-gray-900/5 px-6 pt-4" bis_skin_checked="1"></div><div class="mt-6 flex w-full flex-none gap-x-4 px-6" bis_skin_checked="1"><a hreflang="en" class="flex w-full" href="/image-generator?prompt=user+interface+%2C++game+%2C+for+interaction&amp;ratio=1%3A1&amp;style=Futurism&amp;imageUrl=https%3A%2F%2Fimgcdn.stablediffusionweb.com%2F2024%2F10%2F27%2Fd66de660-7951-4eb6-bb28-c18ef4c6a548.jpg&amp;needSignIn=1"><button class="inline-flex items-center justify-center text-sm font-semibold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 rounded-full px-4 py-2 h-10 w-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all hover:opacity-75"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-wand mr-2 h-6 w-6"><path d="M15 4V2"></path><path d="M15 16v-2"></path><path d="M8 9h2"></path><path d="M20 9h2"></path><path d="M17.8 11.8 19 13"></path><path d="M15 9h0"></path><path d="M17.8 6.2 19 5"></path><path d="m3 21 9-9"></path><path d="M12.2 6.2 11 5"></path></svg>Open in editor</button></a></div><div class="mt-4 flex w-full flex-none gap-x-4 px-6" bis_skin_checked="1"><button class="inline-flex items-center justify-center text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-background focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-transparent hover:bg-accent hover:text-accent-foreground rounded-full px-4 py-2 h-10 w-full"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true" data-slot="icon" class="mr-2 h-6 w-6"><path d="M10.75 2.75a.75.75 0 0 0-1.5 0v8.614L6.295 8.235a.75.75 0 1 0-1.09 1.03l4.25 4.5a.75.75 0 0 0 1.09 0l4.25-4.5a.75.75 0 0 0-1.09-1.03l-2.955 3.129V2.75Z"></path><path d="M3.5 12.75a.75.75 0 0 0-1.5 0v2.5A2.75 2.75 0 0 0 4.75 18h10.5A2.75 2.75 0 0 0 18 15.25v-2.5a.75.75 0 0 0-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5Z"></path></svg>Download</button></div></div></div>