"""
Implementación del almacén vectorial con ChromaDB.
Capa de infraestructura para búsqueda semántica.
"""
import os
import logging
from typing import Optional, List, Dict, Any

import chromadb

from src.infrastructure.config import get_settings
from src.domain.repositories import IVectorStoreRepository

logger = logging.getLogger(__name__)

class ChromaStoreImpl(IVectorStoreRepository):
    """
    Implementación del almacén vectorial usando ChromaDB.
    """
    
    def __init__(self):
        settings = get_settings()
        self._path = settings.vector_store.path
        self._collection_name = settings.vector_store.collection_name
        self._cliente: Optional[chromadb.Client] = None
        self._coleccion: Optional[chromadb.Collection] = None
        
        self._inicializar()
    
    def _inicializar(self) -> None:
        """Inicializa el cliente y la colección de ChromaDB."""
        try:
            os.makedirs(self._path, exist_ok=True)
            self._cliente = chromadb.PersistentClient(path=self._path)
            self._coleccion = self._cliente.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB inicializado: {self._path}, {self._coleccion.count()} documentos")
        except Exception as e:
            logger.error(f"Error al inicializar ChromaDB: {e}", exc_info=True)
            raise
    
    def agregar_documento(self, doc_id: str, texto: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        if not texto or not texto.strip():
            return False
        try:
            metadata_segura = {k: str(v) for k, v in metadata.items() if v is not None} if metadata else {}
            self._coleccion.add(ids=[str(doc_id)], documents=[texto], metadatas=[metadata_segura])
            return True
        except Exception as e:
            logger.error(f"Error al agregar documento: {e}")
            return False
    
    def buscar_semantica(self, query: str, n_resultados: int = 5, filtro: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []
        try:
            resultados = self._coleccion.query(query_texts=[query], n_results=n_resultados, where=filtro)
            documentos = []
            if resultados and resultados.get('ids'):
                ids = resultados['ids'][0]
                docs = resultados.get('documents', [[]])[0]
                metas = resultados.get('metadatas', [[]])[0]
                distancias = resultados.get('distances', [[]])[0]
                for i, doc_id in enumerate(ids):
                    documentos.append({
                        'id': doc_id,
                        'contenido': docs[i] if i < len(docs) else None,
                        'metadata': metas[i] if i < len(metas) else {},
                        'distancia': distancias[i] if i < len(distancias) else None,
                    })
            return documentos
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    def eliminar_documento(self, doc_id: str) -> bool:
        try:
            self._coleccion.delete(ids=[str(doc_id)])
            return True
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")
            return False
    
    def contar_documentos(self) -> int:
        return self._coleccion.count() if self._coleccion else 0
    
    def limpiar_coleccion(self) -> bool:
        try:
            todos = self._coleccion.get()
            if todos and todos.get('ids'):
                self._coleccion.delete(ids=todos['ids'])
            return True
        except Exception as e:
            logger.error(f"Error al limpiar colección: {e}")
            return False
