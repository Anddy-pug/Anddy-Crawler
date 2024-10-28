import requests
import json
import numpy as np

import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(parent_dir)
from setting.setting_manager import *

setting = load_yaml(os.path.abspath(os.path.dirname(__file__) + '/../../crawling_setting/other/embedding.yaml'))

def get_text_embedding(input_text):
    
    # url = "http://192.168.140.246:11434/api/embed"
    url = setting['textembedding_url']
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "bge-m3",
        "input": input_text
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # Attempt to parse the response as JSON
        response_data = json.loads(response.text)
        embeddings = response_data.get('embeddings')
        embeddings_to_flat = np.array(embeddings).flatten().tolist()

        if embeddings is not None:
            # print(embeddings_to_flat)
            return embeddings_to_flat
        else:
            print("No embeddings found in the response.")
            return None
            
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return None
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def get_image_embedding(image_url):

    # url = "http://192.168.140.246:5000/embed_image"  # Adjust the URL as needed
    url = setting['imageembedding_url']
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "image_url": image_url
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        # Attempt to parse the response as JSON
        response_data = json.loads(response.text)
        embeddings = response_data.get('embeddings')

        if embeddings is not None:
            embeddings_to_flat = np.array(embeddings).flatten().tolist()
            # print(embeddings_to_flat)
            return embeddings_to_flat
        else:
            print("No imagefile for embeddings found in the response.")
            return None
            
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)
        return None
    except requests.RequestException as e:
        print("Request failed:", e)
        return None

def custom_text_splitter(text, chunk_size, chunk_overlap):
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks
    
# print(get_image_embedding("http://192.168.140.236:3001/1.jpg"))

# print(get_text_embedding("input_text"))



