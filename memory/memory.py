import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config.settings import MEMORY_COLLECTION


print("🧠 [MEMORY] Inicializando banco de memória vetorial...")

client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="data/memory_db"
    )
)

collection = client.get_or_create_collection(name=MEMORY_COLLECTION)

embedder = SentenceTransformer("all-MiniLM-L6-v2")

print("🧠 [MEMORY] Banco de memória pronto.")


def store_memory(text: str):
    print("🧠 [MEMORY] Armazenando nova memória...")
    embedding = embedder.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[str(hash(text))]
    )

    client.persist()
    print("🧠 [MEMORY] Memória salva com sucesso.")


def recall_memory(query: str, n: int = 5):
    print("🧠 [MEMORY] Buscando memórias relevantes...")

    total = collection.count()

    if total == 0:
        print("🧠 [MEMORY] Nenhuma memória encontrada.")
        return []

    # Nunca pedir mais do que existe
    n_results = min(n, total)

    embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    print(f"🧠 [MEMORY] {n_results} memória(s) recuperada(s).")
    return results["documents"][0]
