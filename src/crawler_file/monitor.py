import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from file_crawler import *
from thumbnail_maker.thumbnail import *
from parser.text_parser import *
import sys
import io
import argparse

# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
# sys.path.append(parent_dir)
# from embedding.embedding import *
# from search_engine.elasticsearch_connector import *
# from thumbnail_maker.thumbnail import *
# from parser.text_parser import *
# from setting.setting_manager import *

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class ChangeHandler(FileSystemEventHandler):
    
    def __init__(self, processor, thumbnail):
        super().__init__()
        self.processor = processor
        self.thumbnail = thumbnail
    
    def file_is_stable(self, file_path, check_interval=1, timeout=30):
        while True: 
            try:
                # Try to open the file in read mode to check for permissions
                with open(file_path, 'rb'): 
                    force_print(f"copy finished: {file_path}")
                    return True  # Permission is granted
            except PermissionError:
                force_print(f"coping file...: {file_path}. checking in {check_interval} seconds...")
                time.sleep(check_interval)  # Wait before retrying

    def on_modified(self, event):
        if not event.is_directory:  # Ignore directory changes
            force_print(f'Modified file: {event.src_path}')

    def on_created(self, event):
        if not event.is_directory:  # Ignore directory changes
            force_print(f'Created file: {event.src_path}')
            if self.file_is_stable(event.src_path):
                try:
                    self.processor.process_file(event.src_path, self.processor.ip)
                    self.thumbnail.create_thumbnail_from_path(event.src_path, self.thumbnail.thumbnail_directory)
                except PermissionError as e:
                    force_print(f"Permission error: {e}")

    def on_deleted(self, event):
        if not event.is_directory:  # Ignore directory changes
            force_print(f'Deleted file: {event.src_path}')
            processor.process_file_delete(event.src_path)
            self.thumbnail.delete_thumbnail_from_path(event.src_path, self.thumbnail.thumbnail_directory)

    def on_moved(self, event):
        if not event.is_directory:  # Ignore directory changes
            force_print(f'Moved file: {event.src_path} to {event.dest_path}')

def start_tika_server():
    tika_server_jar = "tika-server.jar"  # Path to the Tika Server .jar file
    port = 9998  # Port where Tika Server will run
    tika_process = subprocess.Popen(['java', '-jar', tika_server_jar, f'--port={port}'])
    
    # Sleep to give it time to start properly
    time.sleep(5)  # Adjust this if necessary (5 seconds should be enough)
    
    force_print(f"Tika Server started on port {port}")
    return tika_process  # Return the process so we can terminate it later

# Function to stop Tika Server
def stop_tika_server(tika_process):
    tika_process.terminate()  # Terminate the process
    tika_process.wait()  # Wait for the process to exit
    force_print("Tika Server stopped")



if __name__ == "__main__":

    # thumbnail_gen.crawl_directory_and_create_thumbnails(r"F:\______Restult\ElaticSearch\scrapy\tika")

    tika_process = start_tika_server()

    parser = argparse.ArgumentParser(description='File crawler with argument input.')
    parser.add_argument('--crawler_name', type=str, default="default", help="")
    parser.add_argument('--crawler_type', type=str, default="file", help="")

    elastic_config = get_elasticsearch_setting()
    thumbnail_setting = get_thumbnail_setting()
    embedding_setting = get_embedding_setting()
    crawler_setting = get_crawler_setting(parser.parse_args().crawler_name, parser.parse_args().crawler_type)
    
    thumbnail_http_url = 'http://' + get_local_ip() + ':4444/'
    thumbnail_gen = ThumbnailGenerator(thumbnail_setting['thumbnail_url'],
                                       crawler_setting['url'],
                                       thumbnail_http_url,
                                       thumbnail_setting['thumbnail_type'])
    
    http_url = extract_ip_or_default(crawler_setting['url'])
    
    processor = FileProcessor(elastic_config['elasticsearch_url'],
                              elastic_config['elasticsearch_username'],
                              elastic_config['elasticsearch_password'],
                              elastic_config['elasticsearch_fingerprint'],
                              thumbnail_gen,
                              crawler_setting['url'],
                              http_url + ':3001',
                              crawler_setting['indexName'])
    

    directory = r"\\192.168.140.236\search_target"
    
    start_time = time.perf_counter()
    
    directory = crawler_setting['url']
    
    thumbnail_gen.crawl_directory_and_create_thumbnails(directory)
    
    processor.crawl_directory(directory, http_url + ':3001')
    
    end_time = time.perf_counter()
    
    # force_print(get_duration(start_time, end_time))

    # Print or log the duration
    # force_print(f"@@@@@@@@@@@@@@@@@@@@ Execution time: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    
    # thumbnail_gen = ThumbnailGenerator(thumbnail_path=r"F:\______Restult\ElaticSearch\thumbnail\thumbnail",
    #                                    directory = directory)
    # directory = r"\\192.168.140.238\Downloads"
    # thumbnail_gen.crawl_directory_and_create_thumbnails(directory)
    # processor = FileProcessor("https://192.168.140.243:9200",
    #                           "elastic",
    #                           "welcome",
    #                           "4a9cddce08802c5d00cd798d46b7104212b43d2419763324e62a59b8b4ed8168",
    #                           thumbnail_gen, directory,
    #                           "192.168.140.236:3001")

    # processor.crawl_directory(directory, "192.168.140.236:3001")

    # thumbnail_gen = ThumbnailGenerator(thumbnail_path=r"F:\______Restult\ElaticSearch\thumbnail\thumbnail")
    # thumbnail_gen.crawl_directory_and_create_thumbnails(directory)

    event_handler = ChangeHandler(processor, thumbnail_gen)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)

    observer.start()
    force_print(f'Monitoring changes in: {directory}')
    try:
        while True:
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
