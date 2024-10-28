# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '../../../../..'))
sys.path.append(parent_dir)
from embedding.embedding import *
from search_engine.elasticsearch_connector import *
from parser.text_parser import *


class SchoolSpiderPipeline:
    def process_item(self, item, spider):
        return item

from datetime import datetime
import colorama
import logging
from elasticsearch import Elasticsearch, NotFoundError

colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

class ElasticsearchPipeline:
    def __init__(self, es_host, es_port, es_user, es_password, es_index):
        self.es_host = es_host
        self.es_port = es_port
        self.es_user = es_user
        self.es_password = es_password
        self.es_index = es_index
        self.es = None

    @classmethod
    def from_crawler(cls, crawler):
        # Retrieve settings from settings.py
        return cls(
            es_host=crawler.settings.get('ELASTICSEARCH_HOST', 'localhost'),
            es_port=crawler.settings.get('ELASTICSEARCH_PORT', 9200),
            es_user=crawler.settings.get('ELASTICSEARCH_USER', ''),
            es_password=crawler.settings.get('ELASTICSEARCH_PASSWORD', ''),
            es_index=crawler.settings.get('ELASTICSEARCH_INDEX', 'primary_web')
        )

    def open_spider(self, spider):
        # Initialize Elasticsearch client


        # self.es = Elasticsearch(
        #     "https://192.168.140.243:9200",
        #     ssl_assert_fingerprint="31152078dce16528ccd9809dae4c2d18ac285520686aa367de0b2c0a8e309491",
        #     basic_auth=("elastic", "welcome")
        # )
        
        elastic_config = get_elasticsearch_setting()
        

        # elasticsearch_url=elastic_config['elasticsearch_url'],
        # elasticsearch_username=elastic_config['elasticsearch_username'],
        # elasticsearch_password=elastic_config['elasticsearch_password'],
        # elasticsearch_fingerprint=elastic_config['elasticsearch_fingerprint'],
        
        self.es = ElasticsearchConnector(elastic_config['elasticsearch_url'],
                                         elastic_config['elasticsearch_username'],
                                         elastic_config['elasticsearch_password'],
                                         elastic_config['elasticsearch_fingerprint'])

        # Ping to check connection
        # if not self.es.ping():
        #     logging.error("Could not connect to Elasticsearch")
        #     raise ValueError("Connection failed")
        # else:
        #     logging.info("Connected to Elasticsearch")

    def close_spider(self, spider):
        pass
        # Close the Elasticsearch connection
        # if self.es:
        #     self.es.transport.close()
        #     logging.info("Elasticsearch connection closed")

    def process_item(self, item, spider):
        print('###################################################################SPIDER NAME: ' + spider.name)
        if spider.name == 'freelancer_spider':  
            
            document = {
                'title': item['title'],
                'content': item['content'],
                'fields': item['fields'],
                'location': item['location'],
                'price': item['price'],
                'rating': item['rating'],
                'review_count': item['review_count'],
                'payment_verification': item['payment_verification'],
                'member_since': item['member_since'],
                'bid': item['bid'],
            }
            
            self.es.save_data_freelancer(document, 'jobs_freelancer')

            return item
        
        else:
            
            myconfig_value = getattr(spider, 'myconfig', None)
            crawler_setting = get_crawler_setting(myconfig_value, "web")
            # Prepare the document
            content = ""
            content = str(item['content'])
            lang = detect_lang(content)
            texts = custom_text_splitter(content, chunk_size=1500, chunk_overlap=200)
            embedding_title = get_text_embedding(item['title'])
            for i, text in enumerate(texts):
                embedding_content = get_text_embedding(text)
                
                current_time = datetime.now()
                document = {
                    'url': item['url'],
                    'title': item['title'],
                    # 'links': item['links'],
                    'thumbnail': item['favicon'],
                    'content': text,
                    'type': "web",
                    'update': current_time,
                    'embedding_content': embedding_content,
                    'embedding_title': embedding_title,
                    'chunk_id' : i,
                    'lang' : lang
                }
            
            self.es.save_data(document, crawler_setting['indexName'])

            return item
    
