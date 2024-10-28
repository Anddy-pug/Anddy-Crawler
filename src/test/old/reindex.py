import sys
from elasticsearch import Elasticsearch
import requests

def get_existing_documents(es, source_index):
    # Retrieve all documents from the existing index
    scroll = '2m'
    documents = []
    results = es.search(index=source_index, body={"query": {"match_all": {}}}, scroll=scroll, size=1000)
    
    while results['hits']['hits']:
        documents.extend(results['hits']['hits'])
        scroll_id = results['_scroll_id']
        results = es.scroll(scroll_id=scroll_id, scroll=scroll)
    
    return documents

def get_embeddings_from_server(text):
    # Replace with your embedding server URL
    embedding_server_url = "http://localhost:5000/embed_text"
    try:
        response = requests.post(embedding_server_url, json={"query": text})
        response.raise_for_status()
        embeddings = response.json()
        return embeddings['text_embedding']  # Get the text embedding
    except requests.exceptions.RequestException as e:
        print(f"Error contacting embedding server: {e}")
        return None

def custom_text_splitter(text, chunk_size, chunk_overlap):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def main_reindex(source_index, destination_index):
    # Elasticsearch setup
    es = Elasticsearch("https://192.168.140.243:9200",
                       ssl_assert_fingerprint="5c7375ff8f27f77b34410f674e0b000bdd40d2d688408a4357aee962abe96265",
                       basic_auth=("elastic", "welcome")
    )

    # Retrieve documents from the existing index
    documents = get_existing_documents(es, source_index)

    print(f"Reindexing {len(documents)} documents...")

    for doc in documents:
        source = doc['_source']
        file_content = source.get("body_content", "")

        texts = custom_text_splitter(file_content, chunk_size=300, chunk_overlap=30)

        # Get embeddings from the embedding server
        if file_content:
            for i, text in enumerate(texts):
                print(text)
                embedding = get_embeddings_from_server(text)
                doc_body = {
                    # "title": source.get("file", "").get("filename", ""),
                    "title": source.get("title", ""),
                    "content": text,
                    "embedding": embedding,  # Update with new embedding
                    "url": source.get("url", {}),
                    "chunk_id": i
                }
                # Index the updated document into the new index
                es.index(index=destination_index, document=doc_body)
                # es.index(index=destination_index, id=doc['_id'], document=doc_body)

        else:
            embedding = None
        
        # Update the document with the new field
            doc_body = {
                "title": source.get("title", ""),
                "content": file_content,
                "embedding": embedding,  # Update with new embedding
                "url": source.get("url", {})
            }
        
        # # Index the updated document into the new index
        # es.index(index=destination_index, id=doc['_id'], document=doc_body)

    print(f"Finished reindexing to {destination_index}!")

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) > 2:
        source_index = arguments[1]
        destination_index = arguments[2]
        main_reindex(source_index, destination_index)
    else:
        print("You need to provide the source index and destination index as command line arguments")
