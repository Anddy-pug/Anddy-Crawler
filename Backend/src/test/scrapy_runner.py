
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from school_spider import SchoolSpider  # Import your spider here

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from crawler_web.static.school.school_spider.school_spider.spiders.school_spider import ReactSpiderSpider

def run_spider():
    # Get settings from your Scrapy project if needed
    settings = get_project_settings()
    
    # Create a CrawlerProcess instance
    process = CrawlerProcess(settings)
    
    # Run your spider
    process.crawl(ReactSpiderSpider)
    
    # Start the crawling process
    process.start()  # Blocks here until the spider is done

if __name__ == '__main__':
    run_spider()



# Run spider with additional arguments
