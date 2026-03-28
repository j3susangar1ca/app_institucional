import logging
from typing import Optional, Callable
from src.application.use_cases.procesar_documento import ProcesarDocumentoUseCase
from src.application.use_cases.guardar_documento import GuardarDocumentoUseCase
from src.application.dto.documento_dto import DocumentoDTO

logger = logging.getLogger(__name__)

class CorrespondenciaViewModel:
    """ViewModel para la vista de correspondencia (MVVM)."""
    
    def __init__(
        self, 
        procesar_use_case: ProcesarDocumentoUseCase,
        guardar_use_case: GuardarDocumentoUseCase
    ):
        self.procesar_use_case = procesar_use_case
        self.guardar_use_case = guardar_use_case
        
        # Estado de la vista
        self.folio = ""
        self.asunto = ""
        self.contenido = ""
        self.respuesta = ""
        self.ruta_pdf = ""
        self.is_loading = False
        
        # Callbacks para notificar a la vista
        self.on_state_changed: Optional[Callable] = None
        self.on_notification: Optional[Callable] = None

    def set_folio(self, value: str):
        self.folio = value

    def set_asunto(self, value: str):
        self.asunto = value

    def set_contenido(self, value: str):
        self.contenido = value

    def set_respuesta(self, value: str):
        self.respuesta = value

    def update_state(self):
        if self.on_state_changed:
            self.on_state_changed()

    def notify(self, message: str, color: str):
        if self.on_notification:
            self.on_notification(message, color)

    def select_file(self, path: str):
        self.ruta_pdf = path
        self.is_loading = True
        self.update_state()
        
        try:
            texto = self.procesar_use_case.extraer_texto(path)
            self.contenido = texto
            self.notify(f"Archivo cargado: {path.split('/')[-1]}", "green")
        except Exception as e:
            logger.error(f"Error cargando PDF: {str(e)}")
            self.notify(f"Error: {str(e)}", "red")
        finally:
            self.is_loading = False
            self.update_state()

    def generar_respuesta(self):
        if not self.contenido.strip():
            self.notify("Cargue un documento primero", "orange")
            return
            
        self.is_loading = True
        self.respuesta = "Generando respuesta con IA..."
        self.update_state()
        
        try:
            self.respuesta = self.procesar_use_case.generar_respuesta(self.contenido)
            self.notify("Respuesta generada", "green")
        except Exception as e:
            logger.error(f"Error IA: {str(e)}")
            self.notify(f"Error IA: {str(e)}", "red")
        finally:
            self.is_loading = False
            self.update_state()

    def guardar(self):
        if not self.folio or not self.asunto or not self.contenido:
            self.notify("Folio, Asunto y Contenido son requeridos", "orange")
            return
            
        try:
            dto = DocumentoDTO(
                folio=self.folio,
                asunto=self.asunto,
                contenido=self.contenido,
                remitente="Pendiente",
                ruta_archivo=self.ruta_pdf
            )
            self.guardar_use_case.execute(dto)
            self.notify(f"Documento {self.folio} guardado", "green")
        except Exception as e:
            logger.error(f"Error guardando: {str(e)}")
            self.notify(f"Error al guardar: {str(e)}", "red")
