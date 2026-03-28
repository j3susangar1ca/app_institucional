from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class DocumentoDTO:
    id: Optional[int]
    folio: str
    asunto: str
    contenido: str
    fecha: str
    remitente: Optional[str] = None
    ruta_archivo: Optional[str] = None

    @classmethod
    def desde_entidad(cls, e):
        return cls(
            id=e.id,
            folio=e.folio.valor,
            asunto=e.asunto.valor,
            contenido=e.contenido.valor,
            fecha=e.fecha.isoformat(),
            remitente=e.remitente.valor if e.remitente else None,
            ruta_archivo=e.ruta_archivo.valor if e.ruta_archivo else None
        )
    
    def a_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class RespuestaIADTO:
    contenido: str
    modelo: str
    tokens_utilizados: int
    tiempo_respuesta_ms: int

    @classmethod
    def desde_entidad(cls, e):
        return cls(
            contenido=e.contenido,
            modelo=e.modelo,
            tokens_utilizados=e.tokens_utilizados,
            tiempo_respuesta_ms=e.tiempo_respuesta_ms
        )

@dataclass
class ResultadoProcesamientoDTO:
    contenido_extraido: str
    numero_paginas: int
    requiere_ocr: bool
    paginas_con_ocr: List[int]

    @classmethod
    def desde_entidad(cls, e):
        return cls(
            contenido_extraido=e.contenido_extraido,
            numero_paginas=e.numero_paginas,
            requiere_ocr=e.requiere_ocr,
            paginas_con_ocr=list(e.paginas_con_ocr)
        )

@dataclass
class CrearDocumentoRequest:
    folio: str
    asunto: str
    contenido: str
    remitente: Optional[str] = None
    ruta_archivo: Optional[str] = None

@dataclass
class GenerarRespuestaRequest:
    texto_oficio: str
    contexto: Optional[str] = None

@dataclass
class ProcesarPDFRequest:
    ruta_archivo: str

@dataclass
class ResultadoOperacionDTO:
    exitoso: bool
    datos: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    codigo: Optional[str] = None

    @classmethod
    def exitoso(cls, datos: Dict[str, Any]):
        return cls(exitoso=True, datos=datos)

    @classmethod
    def fallido(cls, error: str, codigo: str):
        return cls(exitoso=False, error=error, codigo=codigo)
