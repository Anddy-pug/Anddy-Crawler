import requests
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

img_url = 'http://192.168.140.236/jpg/J0341344.JPG' 
raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')

# conditional image captioning
text = "a photography of"
inputs = processor(raw_image, text, return_tensors="pt")

out = model.generate(**inputs)
print(processor.decode(out[0], skip_special_tokens=True))

# unconditional image captioning
inputs = processor(raw_image, return_tensors="pt")

out = model.generate(**inputs)
print(processor.decode(out[0], skip_special_tokens=True))





import PyPDF2
import os
import sys
from os import listdir
from os.path import isfile, join, isdir, abspath, basename, relpath, getsize
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

def get_files(dir):
    file_list = []
    for f in os.listdir(dir):
        if isfile(join(dir, f)):
            file_list.append(join(dir, f))
        elif isdir(join(dir, f)):
            file_list = file_list + get_files(join(dir, f))
    return file_list

def file_already_indexed(es, file_url):
    # Search for the file URL in the existing index
    search_query = {
        "query": {
            "term": {
                "metadata.url.keyword": file_url  # Use .keyword for exact match
            }
        }
    }
    response = es.search(index="primary-image", body=search_query)
    return len(response['hits']['hits']) > 0

def main_indexing(mypath):
    # Load the SentenceTransformer model for image embeddings from a local directory
    model_path = "./local_clip_model"
    model_name = SentenceTransformer(model_path)

    # Elasticsearch setup
    es = Elasticsearch("https://192.168.140.243:9200",
                       ssl_assert_fingerprint="5c7375ff8f27f77b34410f674e0b000bdd40d2d688408a4357aee962abe96265",
                       basic_auth=("elastic", "welcome")
    )

    # Base URL for Apache
    base_url = "http://192.168.140.236"

    # Supported image formats
    supported_formats = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.avi')

    print("Indexing...")
    onlyfiles = get_files(mypath)
    for file in onlyfiles:
        if file.lower().endswith(supported_formats):
            relative_path = relpath(file, mypath)
            
            # Construct the file URL using the relative path
            file_url = f"{base_url}/{relative_path.replace('\\', '/')}"

            # Check if the file is already indexed
            if file_already_indexed(es, file_url):
                print(f"Skipping already indexed file: {file_url}")
                continue

            print("indexing " + file)
            image_embedding = model_name.encode(file)

            file_name = basename(file)
            file_size = getsize(file)
            metadata = {"filename": file_name, "url": file_url}

            # Elasticsearch indexing
            doc_body = {
                "title": file_name,
                "url": file_url,
                "size": file_size,
                "embedding": image_embedding
            }
            es.index(index="primary-image", document=doc_body)

    print("Finished indexing!")

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) > 1:
        main_indexing(arguments[1])
    else:
        print("You need to provide a path to the folder with documents to index as a command line argument")

# Download and save the model locally (run this part separately before indexing)
# def download_model():
#     model_name = "clip-ViT-B-32"
#     model = SentenceTransformer(model_name)
#     model.save("./local_clip_model")

# if __name__ == "__main__":
#     download_model()
