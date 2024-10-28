from flask import Flask, request, jsonify
from langchain_community.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)

def get_query_embedding(query_text):
    # Local model directory
    model_name = "./local_model"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    hf = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    # Generate embedding for the query text
    texts = [query_text]  # Wrap the query text in a list
    embeddings = hf.embed_documents(texts)
    
    return embeddings[0]  # Return the embedding for the single query text

@app.route('/embed', methods=['POST'])
def embed():
    data = request.json
    query_text = data.get('query')
    
    if not query_text:
        return jsonify({"error": "No query text provided"}), 400
    
    embedding = get_query_embedding(query_text)
    return jsonify({"embedding": embedding})  # Directly return the list

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
