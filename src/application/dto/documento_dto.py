from dataclasses import dataclass
from typing import Optional

@dataclass
class DocumentoDTO:
    """Objeto para transferir datos de documentos entre capas."""
    folio: str
    asunto: str
    contenido: str
    id: Optional[int] = None
    fecha: Optional[str] = None
    remitente: Optional[str] = None
    ruta_archivo: Optional[str] = None

    @classmethod
    def from_domain(cls, entity):
        return cls(
            id=entity.id,
            folio=entity.folio,
            asunto=entity.asunto,
            contenido=entity.contenido,
            fecha=entity.fecha.isoformat() if entity.fecha else None,
            remitente=entity.remitente,
            ruta_archivo=entity.ruta_archivo
        )
