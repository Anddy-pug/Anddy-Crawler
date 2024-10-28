# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SchoolSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class WebContentItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    # links = scrapy.Field()
    favicon = scrapy.Field()
    content = scrapy.Field()
    
    
class FreelancerItem(scrapy.Item):

    title = scrapy.Field()
    content = scrapy.Field()
    fields = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    review_count = scrapy.Field()
    payment_verification = scrapy.Field()
    member_since = scrapy.Field()
    bid = scrapy.Field()