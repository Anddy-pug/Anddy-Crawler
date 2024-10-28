from tika import parser
import os
from datetime import datetime
import concurrent.futures
import subprocess
import time
import sys
import io
import hashlib
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# from elasticsearch_connector import ElasticsearchConnector
# import embedding
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from embedding.embedding import *
from search_engine.elasticsearch_connector import *
from thumbnail_maker.thumbnail import *
from parser.text_parser import *
from setting.setting_manager import *

class FileProcessor:
    def __init__(self, es_url, es_username, es_password, es_fingerprint, thumbnail, url = "/", ip = "127.0.0.1", index_name = "product_file"):
        self.es = ElasticsearchConnector(es_url, es_username, es_password, es_fingerprint)
        self.tika_server_endpoint = 'http://localhost:9998'
        self.document_extensions = ['.pdf', '.docx', '.txt', '.pptx', '.xls', '.csv']
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.url = url
        self.ip = ip
        self.thumbnail = thumbnail
        self.index_name = index_name

    def get_checksum(self, file_path, algorithm='md5'):
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def get_directories(self, directory):
        file_paths = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_extension = os.path.splitext(file)[1].lower()
                if file_extension in self.document_extensions or file_extension in self.image_extensions:
                    file_paths.append(os.path.join(root, file))
        return file_paths

    def get_url(self, file_url):
        relative_url = self.make_relative_directory(file_url, self.url)
        relative_url = relative_url.replace('\\', '/')
        file_url = "http://" + self.ip + "/" + relative_url
        return file_url

    def validate_metadata(self, metadata):
        # Validate date fields
        for date_field in ['created_at', 'modified_at']:
            if metadata.get(date_field) is None:
                metadata[date_field] = "1970-01-01T00:00:00Z"
                # del metadata[date_field]  # Optionally remove the field if it's None

        # Validate numeric fields
        for num_field in ['page_count', 'height', 'width']:
            if metadata.get(num_field) is None:
                metadata[num_field] = 0  # Or set to a default value, or remove the field

        # Ensure 'size' is a number
        if not isinstance(metadata.get('size'), (int, float)):
            metadata['size'] = 0
            

        if not isinstance(metadata.get('width'), (int, float, str)):
            metadata['width'] = 0
            
        if not isinstance(metadata.get('height'), (int, float, str)):
            metadata['height'] = 0

        # Add any additional validations as needed

        return metadata

    def extract_document_metadata(self, file_path, url=None):
        parsed = parser.from_file(file_path, serverEndpoint=self.tika_server_endpoint)
        metadata = parsed.get('metadata', {})
        content = parsed.get('content', '')
        content = clean_text(content)
        checksum = self.get_checksum(file_path)
        lang = detect_lang(content)
        file_name = os.path.basename(file_path)
        relative_url = self.make_relative_directory(file_path, self.url)
        file_extension = os.path.splitext(file_name)[1][1:].lower()
        file_url = "http://" + url + "/" + relative_url
        thumbnail_path = self.thumbnail.http_url + self.thumbnail.make_thumbnail_relative_directory(file_path, self.thumbnail.thumbnail_directory)
        
        created_date = (
            metadata.get('meta:creation-date') or
            metadata.get('Creation-Date') or
            metadata.get('dcterms:created') or
            metadata.get('created') or
            '1970-01-01T00:00:00Z'
        )

        modified_date = (
            metadata.get('Last-Modified') or
            metadata.get('Last_Modified') or
            metadata.get('dcterms:modified') or
            metadata.get('modified') or
            '1970-01-01T00:00:00Z'
        )
        
        extracted_metadata = {
            "title": file_name,
            "type": file_extension,
            "url": file_url,
            "created_at": created_date,
            "modified_at": modified_date,
            "size": round(os.path.getsize(file_path) / (1024), 2),
            "content": content.strip() if content else 'No text content available',
            "thumbnail": thumbnail_path,
            "page_count": metadata.get('xmpTPg:NPages', 0),
            "chunk_id": 0,
            "embedding_title": "",
            "embedding_content": "",
            "height":metadata.get("tiff:ImageLength", 0),
            "width": metadata.get("tiff:ImageWidth", 0),
            "update": "",
            "lang": lang,
            "checksum": checksum
        }
        return self._convert_dates(extracted_metadata)
    
    def make_relative_directory(self, file_path, directory_path):
        relative_path = os.path.relpath(str(file_path), directory_path)
        relative_path = relative_path.replace('\\', '/')
        return relative_path
    
    def extract_image_metadata(self, file_path, url=None):
        parsed = parser.from_file(file_path, serverEndpoint=self.tika_server_endpoint)
        metadata = parsed.get('metadata', {})
        file_name = os.path.basename(file_path)
        relative_url = self.make_relative_directory(file_path, self.url)
        checksum = self.get_checksum(file_path)
        file_extension = os.path.splitext(file_name)[1][1:].lower()
        file_url = "http://" + url + "/" + relative_url
        thumbnail_path = self.thumbnail.http_url + self.thumbnail.make_thumbnail_relative_directory(file_path, self.thumbnail.thumbnail_directory)
        
        created_date = (
            metadata.get('meta:creation-date') or
            metadata.get('Creation-Date') or
            metadata.get('dcterms:created') or
            metadata.get('created') or
            '1970-01-01T00:00:00Z'
        )

        modified_date = (
            metadata.get('Last-Modified') or
            metadata.get('Last_Modified') or
            metadata.get('dcterms:modified') or
            metadata.get('modified') or
            '1970-01-01T00:00:00Z'
        )
        
        extracted_metadata = {
            "title": file_name,
            "type": file_extension,
            "url": file_url,
            "content": "",
            "created_at": created_date,
            "modified_at": modified_date,
            "size": round(os.path.getsize(file_path) / (1024), 2),
            "width": metadata.get("tiff:ImageWidth", 0),
            "height": metadata.get("tiff:ImageLength", 0),
            "thumbnail": thumbnail_path,
            "chunk_id": 0,
            "embedding_content_image": "",
            "lang": "en",
            "checksum": checksum
        }
        return self._convert_dates(extracted_metadata)

    # def process_files(self, file_paths, file_url=None):
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    #         future_to_file = {executor.submit(self.process_file, file_path, file_url): file_path for file_path in file_paths}
    #         for future in concurrent.futures.as_completed(future_to_file):
    #             file_path = future_to_file[future]
    #             try:
    #                 result = future.result()
    #                 force_print(f"Processed {file_path}")
    #             except Exception as exc:
    #                 force_print(f"Error processing {file_path}: {exc}")

    def process_files(self, file_paths, file_url=None):
        
        self.es.create_index(self.index_name + "_document")
        self.es.create_index(self.index_name + "_image")
        
        for file_path in file_paths:
            try:
                self.process_file(file_path, file_url)
                force_print(f"Processed {file_path}")
            except Exception as exc:
                force_print(f"Error processing {file_path}: {exc}")

    def process_file(self, file_path, file_url):
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension in self.document_extensions:
            # pass
            metadata = self.extract_document_metadata(file_path, file_url)
        elif file_extension in self.image_extensions:
            metadata = self.extract_image_metadata(file_path, file_url)
            # self.embed_and_save(metadata)
        else:
            force_print(f"Unsupported file type: {file_path}")
            return
        self.embed_and_save(metadata)
        
    def process_file_delete(self, file_path):
        file_url = self.get_url(file_path)
        indices_to_delete = [self.index_name + "_document", self.index_name + "_image"]
        self.es.remove_data(indices_to_delete, "url", file_url)

    def embed_and_save(self, metadata):
        
        metadata = self.validate_metadata(metadata)  # Add this line
        indices = [self.index_name + "_document", self.index_name + "_image"]
        if self.es.check_document_exists("checksum", metadata['checksum'], indices): 
            force_print(f"{GRAY}[*] Document with ID {metadata['url']} already exists with the same content. Skipping indexing.{RESET}")
        else:
            if metadata["type"] in ['pdf', 'docx', 'txt', 'pptx', 'xls', 'csv']:
                texts = self.custom_text_splitter(metadata["content"], chunk_size=1500, chunk_overlap=200)
                embedding_title = get_text_embedding(metadata["title"])
                for i, text in enumerate(texts):
                    embedding_content = get_text_embedding(text)
                    metadata['embedding_title'] = embedding_title
                    metadata['embedding_content'] = embedding_content
                    metadata['content'] = text
                    metadata['chunk_id'] = i
                    self.es.save_data(metadata, self.index_name + "_document")
            elif metadata["type"] in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
                embedding_title = get_text_embedding(metadata["title"])
                embedding_content = get_image_embedding(metadata['url'])
                metadata['embedding_title'] = embedding_title
                metadata['embedding_content_image'] = embedding_content
                metadata['embedding_content'] = ""
                self.es.save_data(metadata, self.index_name + "_image")

    def custom_text_splitter(self, text, chunk_size, chunk_overlap):
        chunks = []
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def _convert_dates(self, metadata):
        for date_field in ['created_at', 'modified_at']:
            if metadata[date_field] != 'Unknown':
                try:
                    metadata[date_field] = datetime.strptime(metadata[date_field], '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    metadata[date_field] = metadata[date_field]
        return metadata
    
    def crawl_directory(self, directory, ip):
        self.url = directory
        self.ip = ip
        directory_list = self.get_directories(directory)
        self.process_files(directory_list, ip)
    
# processor = FileProcessor("https://192.168.140.243:9200", "elastic", "welcome", "4a9cddce08802c5d00cd798d46b7104212b43d2419763324e62a59b8b4ed8168")

# directory = r"F:\______Restult\ElaticSearch\scrapy\tika"
# file_paths = processor.crawl_directory(directory, "192.168.140.236")
# processor.process_files(file_paths, "192.168.140.236:3001")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='File crawler with argument input.')
    parser.add_argument('--crawler_setting', type=str, default="../crawler_setting/file/default.yaml", help='../crawler_setting/file/default.yaml')
    parser.add_argument('--elastic_setting', type=str, default="../crawler_setting/other/elstic_default.yaml", help='../crawler_setting/other/elstic_default.yaml')
    parser.add_argument('--thumbnail_setting', type=str, default="../crawler_setting/other/thumbnail_default.yaml", help='../crawler_setting/other/thumbnail_default.yaml')
    parser.add_argument('--embedding_setting', type=str, default="../crawler_setting/other/embeeding_default.yaml", help='../crawler_setting/other/embeeding_default.yaml')

    elastic_config = load_yaml(parser.parse_args().elastic_setting)
    thumbnail_setting = load_yaml(parser.parse_args().thumbnail_setting)
    crawler_setting = load_yaml(parser.parse_args().crawler_setting)
    embedding_setting = load_yaml(parser.parse_args().embedding_setting)
    
    processor = FileProcessor(elastic_config['elasticsearch_url'],
                              elastic_config['elasticsearch_username'],
                              elastic_config['elasticsearch_password'],
                              elastic_config['elasticsearch_fingerprint'])
    
    # args = parser.parse_args()

    # Call the main function with parsed arguments
    # main(args.num_threads, args.run_time)
    
    