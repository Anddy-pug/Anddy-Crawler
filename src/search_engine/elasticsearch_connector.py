from elasticsearch import Elasticsearch, NotFoundError
from datetime import datetime
import colorama

colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
# Initialize Elasticsearch client
class ConfigError(Exception):
    """Custom exception for crawler configuration errors."""
    pass

class ElasticsearchConnector:
    def __init__(self, host, username, password, fingerprint):

        self.host = host
        self.username = username
        self.password = password
        self.fingerprint = fingerprint
        self.client = Elasticsearch(
            self.host,
            ssl_assert_fingerprint=self.fingerprint,
            basic_auth=(self.username, self.password)
        )
        if not self.client.ping():
            raise ConfigError("Cannot connect to Elasticsearch.")
        # Check if index exists, if not create it
        # if not self.client.indices.exists(index=self.index):
        #     self.client.indices.create(index=self.index)

    def create_index(self, index_name):

        if self.client.indices.exists(index=index_name):
            print(f"Index '{index_name}' already exists.")
        else:
            # If the index doesn't exist, create it
            self.client.indices.create(index=index_name)
            print(f"Index '{index_name}' created.")

    def check_document_exists(self, field, value, index):
        # Create a search query to find documents with the specified checksum
        query = {
            "query": {
                "match": {
                    field: value
                }
            }
        }

        # Perform the search
        response = self.client.search(index=",".join(index), body=query)



        # Check if any documents were found
        if response['hits']['total']['value'] > 0:
            return True
        else:
            return False

    def save_data(self, metadata, index):
        current_time = datetime.now()
        document = metadata
        # document = {
        #     'url': metadata['url'],
        #     'title': metadata['title'],
        #     'content': metadata['content'],
        #     'thumbnail': metadata['thumbnail'],
        #     'type': metadata['type'],
        #     'update_at': current_time,
        #     'embedding_content': metadata['embedding_content'],
        #     'embedding_title': metadata['embedding_title']
        #     'metadata': "",
        #     'chenk_id' metadata['chenk_id']
        # }
        # if 'lang' in document:
        #     document['lang'] = ""
        document['update'] = current_time
        document['chunk_id'] = int(metadata.get('chunk_id', 0))
        document['size'] = int(metadata.get('size', 0))
        document['width'] = int(metadata.get('width', 0))
        document['height'] = int(metadata.get('height', 0))
        doc_id = document['url'] + "_" + str(document['chunk_id'])
        print(f"{YELLOW}[*] embedding and save metadata {doc_id}.{RESET}")

        try:
            # Check if the document exists
            existing_doc = self.client.get(index=index, id=doc_id)
            
            # If the document exists, you can check its content
            if 'checksum' in existing_doc['_source'] and existing_doc['_source']['checksum'] == document['checksum']:
                print(f"{GRAY}[*] Document with ID {doc_id} already exists with the same content. Skipping indexing.{RESET}")
                # print(f"Document with ID {doc_id} already exists with the same content. Skipping indexing.")
            else:
                # If the content is different, update the document
                self.client.index(index=index, id=doc_id, document=document)
                print(f"{YELLOW}[*] Updated document with ID {doc_id}.{RESET}")
                # print(f"Updated document with ID {doc_id}.")
        except NotFoundError:
            # If the document does not exist, index the new document
            self.client.index(index=index, id=doc_id, document=document)
            # self.client.index(index=index, id=doc_id, document=document, pipeline="elser-v2-document")
            print(f"{GREEN}[*] Indexed new document with ID {doc_id}.{RESET}")
            # print(f"Indexed new document with ID {doc_id}.")
            
    def save_data_freelancer(self, metadata, index):

        self.client.index(index=index, document=metadata)


    def remove_data(self, index, field, value):
        # delete_query = {
        #     "query": {
        #         "match": {
        #             field: value
        #         }
        #     }
        # }   
        delete_query = {
            "query": {
                "term": {
                    field + ".keyword": value
                }
            }
        }   
        # Step 2: Execute the delete_by_query
        response = self.client.delete_by_query(
            index=",".join(index),
            body=delete_query
        )
        
        print(f"{RED}[*] Deleted documents url: {value} , document number {response['deleted']}.{RESET}")

    def get_data(self, document_id):
        """Retrieve data from Elasticsearch by document ID.

        Args:
            document_id (str): The ID of the document to retrieve.

        Returns:
            dict: The document data if found, else None.
        """
        try:
            response = self.client.get(index=self.index, id=document_id)
            return response['_source']  # Return the document source
        except NotFoundError:
            return None  # Document not found