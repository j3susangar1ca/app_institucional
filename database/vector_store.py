import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "./data/chroma_db"

def init_chroma():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name="documentos_institucionales")
    return collection

def add_to_vector_store(doc_id, text, metadata):
    collection = init_chroma()
    collection.add(
        ids=[str(doc_id)],
        documents=[text],
        metadatas=[metadata]
    )

def search_semantic(query, n_results=5):
    collection = init_chroma()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results
