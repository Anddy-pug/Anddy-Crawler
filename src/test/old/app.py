from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import TokenTextSplitter
from transformers import AutoTokenizer

app = Flask(__name__)

# Load models
model_name1 = "./local_model"
model_kwargs1 = {'device': 'cpu'}
encode_kwargs1 = {'normalize_embeddings': True}
hf = HuggingFaceEmbeddings(
    model_name=model_name1,
    model_kwargs=model_kwargs1,
    encode_kwargs=encode_kwargs1
)

model = SentenceTransformer('./local_model')  # Ensure this is the correct path to your model
model_image = SentenceTransformer('./local_clip_model')  # Ensure this is the correct path to your image model

# text = "your_search_term sdafasyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasdyour_search_term sdafasddf"

tokenizer = AutoTokenizer.from_pretrained('./local_model')
# max_length = tokenizer.model_max_length
# print(f"The maximum token length for this model is {max_length}.")

# tokens = tokenizer.tokenize(text)

# Get the number of tokens
# num_tokens = len(tokens)

# print(f"Number of tokens: {num_tokens}")


@app.route('/embed', methods=['POST'])
def embed():
    try:
        data = request.json

        # Ensure 'query' exists in the request data
        if 'query' not in data:
            return jsonify({'error': 'Query field is required'}), 400

        query = data['query']
        
        # Check input length and truncate if necessary
        max_length = 512  # Adjust this based on your model's limits
        tokenized_query = query.split()
        query_length = len(tokenized_query)
        print(f"Received query with {query_length} words.")

        if query_length > max_length:
            print(f"Query exceeds the max length of {max_length} tokens. Truncating the query.")
            query = ' '.join(tokenized_query[:max_length])
        
        # Generate embeddings for text and image
        query_embedding = model.encode([query])[0].tolist()
        query_embedding_image = model_image.encode([query])[0].tolist()

        return jsonify({
            'text_embedding': query_embedding,
            'image_embedding': query_embedding_image
        })
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error to the server console
        return jsonify({'error': str(e)}), 500





@app.route('/embed_textlist', methods=['POST'])
def embed_textlist():
    try:
        data = request.json

        # Ensure 'query' exists in the request data
        if 'query' not in data:
            return jsonify({'error': 'Query field is required'}), 400

        query = data['query']
        
        # Tokenize and split text if necessary
        tokens = tokenizer.tokenize(query)
        max_length = tokenizer.model_max_length
        num_tokens = len(tokens)

        # Split text into chunks if it exceeds the max length
        if num_tokens > max_length:
            chunks = [query[i:i + max_length] for i in range(0, len(query), max_length)]
        else:
            chunks = [query]

        # Generate embeddings for each chunk
        text_embeddings = [model.encode(chunk).tolist() for chunk in chunks]

        return jsonify({
            'text_chunks': chunks,
            'text_embeddings': text_embeddings
        })
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error to the server console
        return jsonify({'error': str(e)}), 500

@app.route('/embed_text', methods=['POST'])
def embed_text():
    try:
        data = request.json

        # Ensure 'query' exists in the request data
        if 'query' not in data:
            return jsonify({'error': 'Query field is required'}), 400

        query = data['query']
        
        # Check input length and truncate if necessary
        max_length = 512  # Adjust this based on your model's limits
        tokenized_query = query.split()
        query_length = len(tokenized_query)
        print(f"Received query with {query_length} words.")

        if query_length > max_length:
            print(f"Query exceeds the max length of {max_length} tokens. Truncating the query.")
            query = ' '.join(tokenized_query[:max_length])
        
        # Generate embeddings using HuggingFaceEmbeddings
        query_embedding = hf.embed_query(query)

        return jsonify({
            'text_embedding': query_embedding
        })
    except Exception as e:
        print(f"Error: {str(e)}")  # Log the error to the server console
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
