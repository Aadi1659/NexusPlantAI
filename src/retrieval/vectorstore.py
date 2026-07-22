import os
import chromadb
from chromadb import EmbeddingFunction
from chromadb.utils.embedding_functions import register_embedding_function
from sentence_transformers import SentenceTransformer

# Define persistent storage path
DB_DIR = "/Users/aadityadevsharma/Documents/hackathon/data/processed/chromadb"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

@register_embedding_function
class LocalEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function wrapper for ChromaDB using SentenceTransformers.
    """
    def __init__(self, model_name=EMBEDDING_MODEL):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        embeddings = self.model.encode(input, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()

    @staticmethod
    def name() -> str:
        return "LocalEmbeddingFunction"

    def get_config(self) -> dict:
        return {"model_name": self.model_name}

    @staticmethod
    def build_from_config(config: dict) -> "LocalEmbeddingFunction":
        return LocalEmbeddingFunction(model_name=config.get("model_name", EMBEDDING_MODEL))

def get_client():
    """
    Returns a persistent ChromaDB client.
    """
    os.makedirs(os.path.dirname(DB_DIR), exist_ok=True)
    return chromadb.PersistentClient(path=DB_DIR)

def get_collection(collection_name):
    """
    Retrieves or creates a ChromaDB collection with local embedding function.
    """
    client = get_client()
    return client.get_or_create_collection(
        name=collection_name,
        embedding_function=LocalEmbeddingFunction()
    )

def add_chunks(collection_name, chunks):
    """
    Adds chunks to the specified ChromaDB collection.
    chunks: List of dicts, each with 'text' and 'metadata'
    """
    if not chunks:
        return
        
    collection = get_collection(collection_name)
    
    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        meta = chunk["metadata"]
        text = chunk["text"]
        
        # Create an idempotent, unique chunk identifier
        if "row_index" in meta:
            # Tabular maintenance/incident logs
            chunk_id = f"{meta['source_file']}_row{meta['row_index']}"
        else:
            # PDF document chunks
            chunk_id = f"{meta['source_file']}_p{meta['page_number']}_c{meta.get('chunk_index', 0)}"
            
        ids.append(chunk_id)
        documents.append(text)
        
        # Clean metadata to contain only types supported by Chroma (str, int, float, bool)
        cleaned_meta = {}
        for k, v in meta.items():
            if v is None:
                cleaned_meta[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                cleaned_meta[k] = v
            else:
                cleaned_meta[k] = str(v)
        metadatas.append(cleaned_meta)
        
    # Batch collection insertions to avoid Chroma limitations
    batch_size = 500
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i+batch_size],
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size]
        )
    print(f"Index Update: Successfully added/updated {len(ids)} items in '{collection_name}'.")

def query_vectorstore(collection_name, query_text, n_results=5, where_filter=None):
    """
    Queries a collection in ChromaDB and returns list of results.
    """
    collection = get_collection(collection_name)
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where_filter
    )
    
    formatted_results = []
    if not results or not results["documents"] or len(results["documents"][0]) == 0:
        return []
        
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
    ids = results["ids"][0]
    
    for idx in range(len(docs)):
        formatted_results.append({
            "id": ids[idx],
            "text": docs[idx],
            "metadata": metas[idx],
            "distance": distances[idx],
            "score": 1.0 - distances[idx]
        })
        
    return formatted_results

def reset_vectorstore():
    """
    Resets the ChromaDB database by deleting existing collections.
    """
    client = get_client()
    for col in client.list_collections():
        print(f"Deleting collection: {col.name}")
        client.delete_collection(col.name)
