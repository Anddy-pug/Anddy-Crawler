import sys
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from langchain_community.embeddings import HuggingFaceEmbeddings
from urllib.parse import urljoin, urlparse
import base64
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import TokenTextSplitter
from elasticsearch import Elasticsearch

def crawl_and_index_url(es, url, hf, image_model, index_name="search-my_elastic", index_name_image="search-my_elastic_image"):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract text content
    text_content = []
    for p in soup.find_all('p'):
        text_content.append(p.get_text())
    page_text = '\n'.join(text_content)

    # Extract and process image content
    for img in soup.find_all('img'):
        img_url = urljoin(url, img['src'])
        try:
            img_response = requests.get(img_url)
            img = Image.open(BytesIO(img_response.content))

            # Encode the image using the SentenceTransformer model
            image_embedding = image_model.encode(img)

            # Construct the image metadata
            metadata = {"url": img_url, "filename": urlparse(img_url).path.split('/')[-1]}

            # Create the Elasticsearch document
            doc_body = {
                "embedding": image_embedding,
                "metadata": metadata
            }

            # Index the image into Elasticsearch
            es.index(index=index_name_image, document=doc_body)

        except Exception as e:
            print(f"Failed to process image {img_url}: {e}")
            continue

    # Extract filename from the URL
    filename = urlparse(url).path.split('/')[-1] or "webpage"

    # Split the text and generate embeddings
    text_splitter = TokenTextSplitter(chunk_size=800, chunk_overlap=80)
    texts = text_splitter.split_text(page_text)
    embeddings = hf.embed_documents(texts)

    # Index text into Elasticsearch
    for i, text in enumerate(texts):
        metadata = {"url": url, "chunk_id": i, "filename": filename}
        doc_body = {
            "content": text,
            "embedding": embeddings[i],
            "metadata": metadata
        }
        es.index(index=index_name, document=doc_body)

    print(f"Finished indexing URL: {url}")

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) > 1:
        url_to_crawl = arguments[1]
        
        # Model and embedding configuration for text
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        hf = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        # Model and embedding configuration for images
        image_model = SentenceTransformer('clip-ViT-B-32')

        # Elasticsearch setup
        es = Elasticsearch("https://192.168.140.243:9200",
                       ssl_assert_fingerprint="5c7375ff8f27f77b34410f674e0b000bdd40d2d688408a4357aee962abe96265",
                       basic_auth=("elastic", "welcome")
        )

        crawl_and_index_url(es, url_to_crawl, hf, image_model)
    else:
        print("You need to provide a URL to crawl and index as a command line argument")
