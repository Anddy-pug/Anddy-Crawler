import multiprocessing
import time
from queue import Empty

# Example function to crawl website and extract meta info
def crawl_and_extract(queue):
    i = 0
    while i < 10:
        # Simulate website crawling and meta info extraction
        meta_info = {"url": f"https://example.com", "title": f"[{i}] Example Title", "content": "This is an example content."}
        
        # Send the meta info to the queue
        queue.put(meta_info)
        print("Crawled and extracted meta info:", meta_info)
        
        time.sleep(5)  # Simulate delay between crawls
        
        i = i + 1

# Example function to process embedding and send to Elasticsearch
def process_and_send_to_es(queue):
    while True:
        try:
            # Get the meta info from the queue
            meta_info = queue.get(timeout=10)  # Wait up to 10 seconds for data
            print("Processing meta info:", meta_info)

            # Generate embedding (example: simulate embedding)
            embedding = f"embedding_of_{meta_info['content']}"

        except Empty:
            print("No data to process")
            break

# Main block to start multiprocessing
if __name__ == '__main__':
    # Create the shared queue
    queue = multiprocessing.Queue()

    # Create the crawling and processing processes
    crawl_process = multiprocessing.Process(target=crawl_and_extract, args=(queue,))
    process_process = multiprocessing.Process(target=process_and_send_to_es, args=(queue,))

    # Start the crawling process
    crawl_process.start()

    # Start the processing and sending to Elasticsearch process
    process_process.start()

    # Join both processes to ensure they complete
    crawl_process.join()
    process_process.join()
