from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.documento import Documento

class IDocumentRepository(ABC):
    """Interfaz para el repositorio de documentos."""
    
    @abstractmethod
    def save(self, documento: Documento) -> Documento:
        """Guarda un documento en el almacén de datos."""
        pass
    
    @abstractmethod
    def get_by_folio(self, folio: str) -> Optional[Documento]:
        """Busca un documento por su folio."""
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100) -> List[Documento]:
        """Obtiene una lista de documentos."""
        pass
