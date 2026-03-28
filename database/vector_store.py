import chromadb
import os
import logging
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

CHROMA_PATH = "./data/chroma_db"


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Crea y retorna un cliente persistente de ChromaDB.
    
    Returns:
        Cliente de ChromaDB configurado
    """
    try:
        # Asegurar que el directorio exista
        os.makedirs(CHROMA_PATH, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        logger.debug(f"Cliente ChromaDB inicializado en {CHROMA_PATH}")
        return client
    except Exception as e:
        logger.error(f"Error al inicializar ChromaDB: {str(e)}", exc_info=True)
        raise e


def init_chroma(collection_name: str = "documentos_institucionales") -> chromadb.Collection:
    """
    Inicializa y retorna una colección de ChromaDB.
    
    Args:
        collection_name: Nombre de la colección
        
    Returns:
        Colección de ChromaDB
    """
    try:
        client = get_chroma_client()
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Similitud por coseno para texto
        )
        logger.info(f"Colección '{collection_name}' inicializada o recuperada")
        return collection
    except Exception as e:
        logger.error(f"Error al inicializar colección ChromaDB: {str(e)}", exc_info=True)
        raise e


def add_to_vector_store(
    doc_id: str, 
    text: str, 
    metadata: Optional[Dict[str, Any]] = None,
    collection_name: str = "documentos_institucionales"
) -> bool:
    """
    Agrega un documento al almacén vectorial.
    
    Args:
        doc_id: Identificador único del documento
        text: Contenido textual del documento
        metadata: Metadatos adicionales (opcional)
        collection_name: Nombre de la colección
        
    Returns:
        True si se agregó exitosamente, False en caso contrario
    """
    if not text or not text.strip():
        logger.warning("Intento de agregar documento vacío al vector store")
        return False
    
    try:
        collection = init_chroma(collection_name)
        
        # Preparar metadatos por defecto si no se proporcionan
        if metadata is None:
            metadata = {}
        
        # Asegurar que los metadatos solo contengan tipos serializables
        safe_metadata = {k: str(v) for k, v in metadata.items() if v is not None}
        
        collection.add(
            ids=[str(doc_id)],
            documents=[text],
            metadatas=[safe_metadata]
        )
        
        logger.info(f"Documento {doc_id} agregado al vector store")
        return True
        
    except Exception as e:
        logger.error(f"Error al agregar documento al vector store: {str(e)}", exc_info=True)
        return False


def search_semantic(
    query: str, 
    n_results: int = 5,
    collection_name: str = "documentos_institucionales",
    where_filter: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Realiza una búsqueda semántica en el almacén vectorial.
    
    Args:
        query: Texto de consulta
        n_results: Número máximo de resultados a retornar
        collection_name: Nombre de la colección
        where_filter: Filtro opcional para metadatos
        
    Returns:
        Diccionario con los resultados de la búsqueda
    """
    if not query or not query.strip():
        logger.warning("Búsqueda semántica con consulta vacía")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}
    
    try:
        collection = init_chroma(collection_name)
        
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, 100),  # Límite máximo razonable
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        logger.debug(f"Búsqueda semántica completada: {len(results.get('ids', [[]])[0])} resultados")
        return results
        
    except Exception as e:
        logger.error(f"Error en búsqueda semántica: {str(e)}", exc_info=True)
        return {"ids": [], "documents": [], "metadatas": [], "distances": [], "error": str(e)}


def delete_from_vector_store(
    doc_id: str,
    collection_name: str = "documentos_institucionales"
) -> bool:
    """
    Elimina un documento del almacén vectorial.
    
    Args:
        doc_id: Identificador del documento a eliminar
        collection_name: Nombre de la colección
        
    Returns:
        True si se eliminó exitosamente, False en caso contrario
    """
    try:
        collection = init_chroma(collection_name)
        collection.delete(ids=[str(doc_id)])
        logger.info(f"Documento {doc_id} eliminado del vector store")
        return True
    except Exception as e:
        logger.error(f"Error al eliminar documento del vector store: {str(e)}", exc_info=True)
        return False
