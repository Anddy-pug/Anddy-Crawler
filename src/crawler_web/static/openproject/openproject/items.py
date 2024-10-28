# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OpenprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class WebContentItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    # links = scrapy.Field()
    favicon = scrapy.Field()
    p = scrapy.Field()