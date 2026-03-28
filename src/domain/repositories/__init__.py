from typing import Protocol, List, Dict, Any, Optional, runtime_checkable

@runtime_checkable
class IVectorStoreRepository(Protocol):
    """Protocolo para el almacén vectorial."""
    
    def agregar_documento(
        self,
        doc_id: str,
        texto: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool: ...
    
    def buscar_semantica(
        self,
        query: str,
        n_resultados: int = 5,
        filtro: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]: ...
    
    def eliminar_documento(self, doc_id: str) -> bool: ...
    def contar_documentos(self) -> int: ...
    def limpiar_coleccion(self) -> bool: ...
