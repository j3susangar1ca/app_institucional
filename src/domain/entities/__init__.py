from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Generic, TypeVar, List, Set
from ..value_objects import Folio, Asunto, ContenidoTexto, Remitente, RutaArchivo

T = TypeVar('T')

@dataclass
class ResultadoOperacion(Generic[T]):
    """Resultado genérico para operaciones de dominio."""
    exitoso: bool
    datos: Optional[T] = None
    error: Optional[str] = None
    codigo_error: Optional[str] = None

    def es_exitoso(self) -> bool:
        return self.exitoso

@dataclass
class RespuestaIA:
    """Entidad que representa una respuesta generada por IA."""
    contenido: str
    modelo: str
    tokens_utilizados: int = 0
    tiempo_respuesta_ms: int = 0

@dataclass
class ResultadoProcesamientoPDF:
    """Entidad que representa el resultado de procesar un PDF."""
    contenido_extraido: str
    numero_paginas: int
    requiere_ocr: bool = False
    paginas_con_ocr: Set[int] = field(default_factory=set)

@dataclass
class Documento:
    """Entidad de dominio principal para documentos."""
    folio: Folio
    asunto: Asunto
    contenido: ContenidoTexto
    remitente: Optional[Remitente] = None
    ruta_archivo: Optional[RutaArchivo] = None
    id: Optional[int] = None
    fecha: datetime = field(default_factory=datetime.utcnow)
