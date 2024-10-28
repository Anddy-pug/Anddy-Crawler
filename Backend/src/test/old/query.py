import sys
from langchain_community.embeddings import HuggingFaceEmbeddings

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

if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) > 1:
        query_text = " ".join(arguments[1:])
        embedding = get_query_embedding(query_text)
        print("Embedding result for query:", embedding)
    else:
        print("You need to provide a query text as a command line argument.")
