from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Documento:
    """Entidad de dominio que representa un documento institucional."""
    
    folio: str
    asunto: str
    contenido: str
    id: Optional[int] = None
    fecha: datetime = field(default_factory=datetime.utcnow)
    remitente: Optional[str] = None
    ruta_archivo: Optional[str] = None

    def __post_init__(self):
        if not self.folio or not self.folio.strip():
            raise ValueError("El folio no puede estar vacío")
        if not self.asunto or not self.asunto.strip():
            raise ValueError("El asunto no puede estar vacío")
        if not self.contenido or not self.contenido.strip():
            raise ValueError("El contenido no puede estar vacío")
