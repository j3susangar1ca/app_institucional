import flet as ft
import logging
from src.infrastructure.config import get_settings
from src.infrastructure.persistence.sql_document_repository import DocumentoRepositoryImpl
from src.infrastructure.pdf.procesador_pdf import PDFProcessorImpl
from src.infrastructure.ai.ia_cliente import OpenAIClientImpl
from src.infrastructure.vector_store.chroma_store import ChromaStoreImpl
from src.application.use_cases import (
    CargarDocumentoUseCase, GenerarRespuestaUseCase, GuardarDocumentoUseCase, BuscarDocumentoUseCase
)
from src.presentation.flet.viewmodels.correspondencia_viewmodel import CorrespondenciaViewModel
from src.presentation.flet.views.correspondencia_view import CorrespondenciaView

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    settings = get_settings()
    
    # Infraestructura
    repo = DocumentoRepositoryImpl()
    repo.inicializar()
    
    pdf = PDFProcessorImpl(idioma_ocr=settings.ocr_language)
    ia = OpenAIClientImpl(settings=settings.ai)
    vector_store = ChromaStoreImpl()
    
    # Aplicación
    cargar_uc = CargarDocumentoUseCase(pdf)
    generar_uc = GenerarRespuestaUseCase(ia)
    guardar_uc = GuardarDocumentoUseCase(repo)
    
    # Presentación
    vm = CorrespondenciaViewModel(cargar_uc, generar_uc, guardar_uc)
    
    # Configuración Page
    page.title = settings.app_name
    page.window.width = settings.ui.window_width
    page.window.height = settings.ui.window_height
    page.theme_mode = ft.ThemeMode.LIGHT if settings.ui.theme_mode == "light" else ft.ThemeMode.DARK
    page.padding = settings.ui.padding
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)

    # Vista
    view = CorrespondenciaView(page, vm)
    page.add(view)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
