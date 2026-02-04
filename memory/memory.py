import chromadb
from sentence_transformers import SentenceTransformer
from config.settings import MEMORY_COLLECTION

client = chromadb.Client(
    settings=chromadb.Settings(persist_directory="data/memory_db")
)

collection = client.get_or_create_collection(MEMORY_COLLECTION)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def store_memory(text: str):
    embedding = embedder.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(hash(text))]
    )
    client.persist()

def recall_memory(query: str, n: int = 5):
    if collection.count() == 0:
        return []

    embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n
    )
    return results["documents"][0]
