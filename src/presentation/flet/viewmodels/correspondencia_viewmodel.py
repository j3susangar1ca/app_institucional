import logging
from typing import Optional, Callable
from src.application.use_cases import (
    CargarDocumentoUseCase, GenerarRespuestaUseCase, GuardarDocumentoUseCase,
    ProcesarPDFRequest, GenerarRespuestaRequest, CrearDocumentoRequest
)

logger = logging.getLogger(__name__)

class CorrespondenciaViewModel:
    """ViewModel para la vista de correspondencia (MVVM)."""
    
    def __init__(
        self, 
        cargar_uc: CargarDocumentoUseCase,
        generar_uc: GenerarRespuestaUseCase,
        guardar_uc: GuardarDocumentoUseCase
    ):
        self.cargar_uc = cargar_uc
        self.generar_uc = generar_uc
        self.guardar_uc = guardar_uc
        
        # Estado
        self.folio = ""
        self.asunto = ""
        self.contenido = ""
        self.respuesta = ""
        self.ruta_pdf = ""
        self.is_loading = False
        
        self.on_state_changed: Optional[Callable] = None
        self.on_notification: Optional[Callable] = None

    def set_folio(self, v: str): self.folio = v
    def set_asunto(self, v: str): self.asunto = v
    def set_contenido(self, v: str): self.contenido = v
    def set_respuesta(self, v: str): self.respuesta = v

    def update_state(self):
        if self.on_state_changed: self.on_state_changed()

    def notify(self, msg: str, color: str):
        if self.on_notification: self.on_notification(msg, color)

    def select_file(self, path: str):
        self.ruta_pdf = path
        self.is_loading = True
        self.update_state()
        
        try:
            req = ProcesarPDFRequest(ruta_archivo=path)
            res = self.cargar_uc.ejecutar(req)
            
            if res.exitoso:
                self.contenido = res.datos['contenido']
                self.notify(f"Archivo cargado ({res.datos['numero_paginas']} págs)", "green")
            else:
                self.notify(f"Error: {res.error}", "red")
        except Exception as e:
            self.notify(f"Error crítico: {str(e)}", "red")
        finally:
            self.is_loading = False
            self.update_state()

    def generar_respuesta(self):
        if not self.contenido.strip():
            return self.notify("Cargue documento primero", "orange")
            
        self.is_loading = True
        self.update_state()
        
        try:
            req = GenerarRespuestaRequest(texto_oficio=self.contenido)
            res = self.generar_uc.ejecutar(req)
            
            if res.exitoso:
                self.respuesta = res.datos['contenido']
                self.notify("Respuesta generada", "green")
            else:
                self.notify(f"Error IA: {res.error}", "red")
        except Exception as e:
            self.notify(f"Error IA: {str(e)}", "red")
        finally:
            self.is_loading = False
            self.update_state()

    def guardar(self):
        if not self.folio or not self.asunto:
            return self.notify("Folio y Asunto requeridos", "orange")
            
        try:
            req = CrearDocumentoRequest(
                folio=self.folio, asunto=self.asunto, contenido=self.contenido,
                remitente="Enviado por IA", ruta_archivo=self.ruta_pdf
            )
            res = self.guardar_uc.ejecutar(req)
            
            if res.exitoso:
                self.notify(f"Guardado como {res.datos['id']}", "green")
            else:
                self.notify(f"Error: {res.error}", "red")
        except Exception as e:
            self.notify(f"Error al guardar: {str(e)}", "red")
