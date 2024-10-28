# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class OpenprojectPipeline:
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
            es_index=crawler.settings.get('ELASTICSEARCH_INDEX', 'web-content-openproject')
        )

    def open_spider(self, spider):
        # Initialize Elasticsearch client


        self.es = Elasticsearch(
            "https://192.168.140.243:9200",
            ssl_assert_fingerprint="31152078dce16528ccd9809dae4c2d18ac285520686aa367de0b2c0a8e309491",
            basic_auth=("elastic", "welcome")
        )

        # Ping to check connection
        if not self.es.ping():
            logging.error("Could not connect to Elasticsearch")
            raise ValueError("Connection failed")
        else:
            logging.info("Connected to Elasticsearch")

    def close_spider(self, spider):
        # Close the Elasticsearch connection
        if self.es:
            self.es.transport.close()
            logging.info("Elasticsearch connection closed")

    def process_item(self, item, spider):
        # Prepare the document
        current_time = datetime.now()
        document = {
            'url': item['url'],
            'title': item['title'],
            # 'links': item['links'],
            'thumbnail': item['favicon'],
            'content': item['p'],
            'type': "web",
            'update_at': current_time,
            'embedding_content': "",
            'embedding_title': ""
        }

        doc_id = item['url']

        try:
            # Check if the document exists
            existing_doc = self.es.get(index=self.es_index, id=doc_id)
            
            # If the document exists, you can check its content
            if existing_doc['_source']['content'] == document['content']:
                print(f"{GRAY}[*] Document with ID {doc_id} already exists with the same content. Skipping indexing. {RESET}")
                # print(f"Document with ID {doc_id} already exists with the same content. Skipping indexing.")
            else:
                # If the content is different, update the document
                self.es.index(index=self.es_index, id=doc_id, document=document)
                print(f"{YELLOW}[*] Updated document with ID {doc_id}. {RESET}")
                # print(f"Updated document with ID {doc_id}.")
        except NotFoundError:
            # If the document does not exist, index the new document
            self.es.index(index=self.es_index, id=doc_id, document=document)
            print(f"{GREEN}[*] Indexed new document with ID {doc_id}. {RESET}")
            # print(f"Indexed new document with ID {doc_id}.")


        return item