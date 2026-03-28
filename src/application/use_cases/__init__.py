"""
Use Cases de la capa de aplicación.
Orquestan el flujo de datos y ejecutan lógica de negocio.
"""
from dataclasses import dataclass
import time
from typing import Optional, Protocol, runtime_checkable
from ..domain.entities import Documento, RespuestaIA, ResultadoProcesamientoPDF, ResultadoOperacion
from ..domain.value_objects import Folio, Asunto, ContenidoTexto, Remitente, RutaArchivo
from .dto import (
    DocumentoDTO, RespuestaIADTO, ResultadoProcesamientoDTO,
    CrearDocumentoRequest, GenerarRespuestaRequest, ProcesarPDFRequest,
    ResultadoOperacionDTO
)


@runtime_checkable
class IDocumentoRepository(Protocol):
    """Protocolo para el repositorio de documentos."""
    
    def guardar(self, documento: Documento) -> Documento: ...
    def buscar_por_folio(self, folio: str) -> Optional[Documento]: ...
    def existe_folio(self, folio: str) -> bool: ...
    def listar_todos(self, limite: int = 100) -> list[Documento]: ...


@runtime_checkable
class IServicioIA(Protocol):
    """Protocolo para el servicio de IA."""
    
    def generar_respuesta(
        self, 
        texto_oficio: str, 
        contexto: Optional[str] = None
    ) -> ResultadoOperacion[RespuestaIA]: ...


@runtime_checkable
class IServicioProcesadorPDF(Protocol):
    """Protocolo para el procesador de PDF."""
    
    def procesar_pdf(self, ruta: str) -> ResultadoOperacion[ResultadoProcesamientoPDF]: ...
    def validar_archivo(self, ruta: str) -> bool: ...


class CargarDocumentoUseCase:
    """
    Use Case para cargar y procesar documentos PDF.
    """
    
    def __init__(self, procesador_pdf: IServicioProcesadorPDF):
        self._procesador = procesador_pdf
    
    def ejecutar(self, request: ProcesarPDFRequest) -> ResultadoOperacionDTO:
        # Validar archivo
        if not self._procesador.validar_archivo(request.ruta_archivo):
            return ResultadoOperacionDTO.fallido(
                "El archivo no existe o no es un PDF válido",
                "ARCHIVO_INVALIDO"
            )
        
        # Procesar PDF
        resultado = self._procesador.procesar_pdf(request.ruta_archivo)
        
        if not resultado.es_exitoso():
            return ResultadoOperacionDTO.fallido(
                resultado.error or "Error al procesar el PDF",
                "ERROR_PROCESAMIENTO"
            )
        
        # Convertir a DTO
        dto = ResultadoProcesamientoDTO.desde_entidad(resultado.datos)
        
        return ResultadoOperacionDTO.exitoso({
            'contenido': dto.contenido_extraido,
            'numero_paginas': dto.numero_paginas,
            'requiere_ocr': dto.requiere_ocr,
            'paginas_ocr': list(dto.paginas_con_ocr),
            'ruta_archivo': request.ruta_archivo,
        })


class GenerarRespuestaUseCase:
    """
    Use Case para generar respuestas con IA.
    """
    
    def __init__(self, servicio_ia: IServicioIA):
        self._servicio_ia = servicio_ia
    
    def ejecutar(self, request: GenerarRespuestaRequest) -> ResultadoOperacionDTO:
        # Validar entrada
        if not request.texto_oficio or not request.texto_oficio.strip():
            return ResultadoOperacionDTO.fallido(
                "El texto del oficio no puede estar vacío",
                "TEXTO_VACIO"
            )
        
        # Generar respuesta
        resultado = self._servicio_ia.generar_respuesta(
            texto_oficio=request.texto_oficio,
            contexto=request.contexto
        )
        
        if not resultado.es_exitoso():
            return ResultadoOperacionDTO.fallido(
                resultado.error or "Error al generar respuesta",
                "ERROR_IA"
            )
        
        # Convertir a DTO
        dto = RespuestaIADTO.desde_entidad(resultado.datos)
        
        return ResultadoOperacionDTO.exitoso({
            'contenido': dto.contenido,
            'modelo': dto.modelo,
            'tokens': dto.tokens_utilizados,
            'tiempo_ms': dto.tiempo_respuesta_ms,
        })


class GuardarDocumentoUseCase:
    """
    Use Case para guardar documentos en la base de datos.
    """
    
    def __init__(self, repositorio: IDocumentoRepository):
        self._repositorio = repositorio
    
    def ejecutar(self, request: CrearDocumentoRequest) -> ResultadoOperacionDTO:
        try:
            # Crear Value Objects (validación implícita)
            folio = Folio(request.folio)
            asunto = Asunto(request.asunto)
            contenido = ContenidoTexto(request.contenido)
            remitente = Remitente(request.remitente)
            
            # Verificar folio único
            if self._repositorio.existe_folio(request.folio):
                return ResultadoOperacionDTO.fallido(
                    f"Ya existe un documento con el folio '{request.folio}'",
                    "FOLIO_DUPLICADO"
                )
            
            # Crear ruta de archivo si existe
            ruta_archivo = None
            if request.ruta_archivo:
                ruta_archivo = RutaArchivo(request.ruta_archivo)
            
            # Crear entidad de dominio
            documento = Documento(
                folio=folio,
                asunto=asunto,
                contenido=contenido,
                remitente=remitente,
                ruta_archivo=ruta_archivo,
            )
            
            # Persistir
            documento_guardado = self._repositorio.guardar(documento)
            
            # Convertir a DTO
            dto = DocumentoDTO.desde_entidad(documento_guardado)
            
            return ResultadoOperacionDTO.exitoso(dto.a_dict())
            
        except ValueError as e:
            return ResultadoOperacionDTO.fallido(str(e), "VALIDACION_ERROR")
        except Exception as e:
            return ResultadoOperacionDTO.fallido(f"Error inesperado al guardar: {str(e)}", "ERROR_INTERNO")


class BuscarDocumentoUseCase:
    """
    Use Case para buscar documentos.
    """
    
    def __init__(self, repositorio: IDocumentoRepository):
        self._repositorio = repositorio
    
    def buscar_por_folio(self, folio: str) -> ResultadoOperacionDTO:
        documento = self._repositorio.buscar_por_folio(folio)
        
        if not documento:
            return ResultadoOperacionDTO.fallido(
                f"No se encontró documento con folio '{folio}'",
                "DOCUMENTO_NO_ENCONTRADO"
            )
        
        dto = DocumentoDTO.desde_entidad(documento)
        return ResultadoOperacionDTO.exitoso(dto.a_dict())
    
    def listar_todos(self, limite: int = 100) -> ResultadoOperacionDTO:
        documentos = self._repositorio.listar_todos(limite=limite)
        lista_dto = [DocumentoDTO.desde_entidad(d).a_dict() for d in documentos]
        return ResultadoOperacionDTO.exitoso({
            'documentos': lista_dto,
            'total': len(lista_dto),
        })
