"""
ViewModel para la gestión de correspondencia.
Implementa el patrón MVVM para separar lógica de UI.
"""
from dataclasses import dataclass, field
from typing import Optional, Callable, List
from enum import Enum
import logging

from src.application.use_cases import (
    CargarDocumentoUseCase,
    GenerarRespuestaUseCase,
    GuardarDocumentoUseCase,
    BuscarDocumentoUseCase,
)
from src.application.dto import (
    CrearDocumentoRequest,
    GenerarRespuestaRequest,
    ProcesarPDFRequest,
)

logger = logging.getLogger(__name__)

class EstadoVista(Enum):
    """Estados posibles de la vista."""
    INACTIVO = "inactivo"
    CARGANDO = "cargando"
    PROCESANDO_PDF = "procesando_pdf"
    GENERANDO_RESPUESTA = "generando_respuesta"
    GUARDANDO = "guardando"
    ERROR = "error"
    EXITO = "exito"

@dataclass
class CorrespondenciaState:
    estado: EstadoVista = EstadoVista.INACTIVO
    folio: str = ""
    asunto: str = ""
    contenido_oficio: str = ""
    contenido_respuesta: str = ""
    ruta_pdf_actual: str = ""
    mensaje: str = ""
    mensaje_error: str = ""
    numero_paginas: int = 0
    requiere_ocr: bool = False
    documentos_recientes: List[dict] = field(default_factory=list)

class CorrespondenciaViewModel:
    def __init__(
        self,
        cargar_doc_use_case: CargarDocumentoUseCase,
        generar_respuesta_use_case: GenerarRespuestaUseCase,
        guardar_doc_use_case: GuardarDocumentoUseCase,
        buscar_doc_use_case: BuscarDocumentoUseCase,
    ):
        self._cargar_doc = cargar_doc_use_case
        self._generar_respuesta = generar_respuesta_use_case
        self._guardar_doc = guardar_doc_use_case
        self._buscar_doc = buscar_doc_use_case
        self._state = CorrespondenciaState()
        self._on_state_change: Optional[Callable[[CorrespondenciaState], None]] = None
    
    @property
    def state(self) -> CorrespondenciaState:
        return self._state
    
    def set_on_state_change(self, callback: Callable[[CorrespondenciaState], None]) -> None:
        self._on_state_change = callback
    
    def _notificar_cambio(self) -> None:
        if self._on_state_change:
            self._on_state_change(self._state)
    
    def _set_estado(self, nuevo_estado: EstadoVista) -> None:
        self._state.estado = nuevo_estado
        self._notificar_cambio()
    
    def _set_error(self, mensaje: str) -> None:
        self._state.mensaje_error = mensaje
        self._state.mensaje = ""
        self._set_estado(EstadoVista.ERROR)
    
    def _set_mensaje(self, mensaje: str) -> None:
        self._state.mensaje = mensaje
        self._state.mensaje_error = ""
        self._set_estado(EstadoVista.EXITO)
    
    def actualizar_folio(self, valor: str) -> None:
        self._state.folio = valor.strip().upper()
        self._notificar_cambio()
    
    def actualizar_asunto(self, valor: str) -> None:
        self._state.asunto = valor.strip()
        self._notificar_cambio()
    
    def actualizar_contenido_oficio(self, valor: str) -> None:
        self._state.contenido_oficio = valor
        self._notificar_cambio()
    
    def procesar_pdf(self, ruta_archivo: str) -> None:
        self._set_estado(EstadoVista.PROCESANDO_PDF)
        self._state.ruta_pdf_actual = ruta_archivo
        res = self._cargar_doc.ejecutar(ProcesarPDFRequest(ruta_archivo=ruta_archivo))
        if res.exito:
            self._state.contenido_oficio = res.datos['contenido']
            self._state.numero_paginas = res.datos['numero_paginas']
            self._state.requiere_ocr = res.datos['requiere_ocr']
            self._set_mensaje(f"PDF procesado: {res.datos['numero_paginas']} págs")
        else:
            self._set_error(res.error or "Error PDF")
    
    def generar_respuesta(self) -> None:
        if not self._state.contenido_oficio.strip():
            return self._set_error("No hay contenido")
        self._set_estado(EstadoVista.GENERANDO_RESPUESTA)
        self._state.contenido_respuesta = "Generando..."
        self._notificar_cambio()
        res = self._generar_respuesta.ejecutar(GenerarRespuestaRequest(
            texto_oficio=self._state.contenido_oficio,
            contexto=self._state.asunto
        ))
        if res.exito:
            self._state.contenido_respuesta = res.datos['contenido']
            self._set_mensaje("Respuesta generada")
        else:
            self._set_error(res.error or "Error IA")
    
    def guardar_documento(self) -> None:
        if not self._state.folio: return self._set_error("Folio requerido")
        if not self._state.asunto: return self._set_error("Asunto requerido")
        self._set_estado(EstadoVista.GUARDANDO)
        res = self._guardar_doc.ejecutar(CrearDocumentoRequest(
            folio=self._state.folio,
            asunto=self._state.asunto,
            contenido=self._state.contenido_oficio,
            ruta_archivo=self._state.ruta_pdf_actual
        ))
        if res.exito:
            self._set_mensaje(f"Guardado: {self._state.folio}")
            self._limpiar_formulario()
        else:
            self._set_error(res.error or "Error guardar")

    def _limpiar_formulario(self) -> None:
        self._state.folio = ""
        self._state.asunto = ""
        self._state.contenido_oficio = ""
        self._state.contenido_respuesta = ""
        self._state.ruta_pdf_actual = ""
        self._notificar_cambio()

    def limpiar_estado(self) -> None:
        self._state = CorrespondenciaState()
        self._set_estado(EstadoVista.INACTIVO)
