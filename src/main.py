"""
Punto de entrada principal de la aplicación.
Implementa inyección de dependencias y configuración inicial.
"""
import logging
import sys
import flet as ft

from src.infrastructure.config import get_settings
from src.infrastructure.persistence.sql_document_repository import DocumentoRepositoryImpl
from src.infrastructure.ai.ia_cliente import OpenAIClientImpl
from src.infrastructure.pdf.procesador_pdf import PDFProcessorImpl
from src.infrastructure.vector_store.chroma_store import ChromaStoreImpl
from src.application.use_cases import (
    CargarDocumentoUseCase,
    GenerarRespuestaUseCase,
    GuardarDocumentoUseCase,
    BuscarDocumentoUseCase,
)
from src.presentation.flet.viewmodels.correspondencia_vm import CorrespondenciaViewModel
from src.presentation.flet.views.correspondencia_view import CorrespondenciaView

def configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

class Container:
    """Contenedor de inyección de dependencias."""
    def __init__(self):
        self._settings = get_settings()
        self._inicializar_infraestructura()
        self._inicializar_use_cases()
    
    def _inicializar_infraestructura(self) -> None:
        self._documento_repo = DocumentoRepositoryImpl()
        self._documento_repo.inicializar()
        self._ia_cliente = OpenAIClientImpl()
        self._pdf_processor = PDFProcessorImpl(idioma_ocr='spa')
        self._vector_store = ChromaStoreImpl()
    
    def _inicializar_use_cases(self) -> None:
        self._cargar_doc_use_case = CargarDocumentoUseCase(self._pdf_processor)
        self._generar_respuesta_use_case = GenerarRespuestaUseCase(self._ia_cliente)
        self._guardar_doc_use_case = GuardarDocumentoUseCase(self._documento_repo)
        self._buscar_doc_use_case = BuscarDocumentoUseCase(self._documento_repo)
    
    def get_viewmodel(self) -> CorrespondenciaViewModel:
        return CorrespondenciaViewModel(
            self._cargar_doc_use_case,
            self._generar_respuesta_use_case,
            self._guardar_doc_use_case,
            self._buscar_doc_use_case
        )
    
    def get_settings(self): return self._settings

def main(page: ft.Page) -> None:
    configurar_logging()
    logger = logging.getLogger(__name__)
    try:
        container = Container()
        settings = container.get_settings()
        
        page.title = settings.app_name
        page.window.width = settings.ui.window_width
        page.window.height = settings.ui.window_height
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = settings.ui.padding
        page.bgcolor = ft.Colors.BLUE_GREY_50
        page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)
        
        viewmodel = container.get_viewmodel()
        vista = CorrespondenciaView(page, viewmodel)
        page.add(vista)
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar: {e}", exc_info=True)
        page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))

if __name__ == "__main__":
    ft.app(target=main)
