import flet as ft
import logging
from src.infrastructure.persistence.database import init_db
from src.infrastructure.persistence.sql_document_repository import SqlAlchemyDocumentRepository
from src.infrastructure.pdf.procesador_pdf import ProcesadorPDF
from src.infrastructure.ai.ia_cliente import IACliente
from src.application.use_cases.procesar_documento import ProcesarDocumentoUseCase
from src.application.use_cases.guardar_documento import GuardarDocumentoUseCase
from src.presentation.flet.viewmodels.correspondencia_viewmodel import CorrespondenciaViewModel
from src.presentation.flet.views.correspondencia_view import CorrespondenciaView
from src.infrastructure.config import get_settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    settings = get_settings()
    
    # 1. Inicializar Infraestructura
    init_db()
    
    # Dependencias
    repository = SqlAlchemyDocumentRepository()
    procesador = ProcesadorPDF()
    ia = IACliente()
    
    # 2. Inicializar Aplicación (Casos de Uso)
    procesar_uc = ProcesarDocumentoUseCase(procesador, ia)
    guardar_uc = GuardarDocumentoUseCase(repository)
    
    # 3. Inicializar Presentación (ViewModel y View)
    vm = CorrespondenciaViewModel(procesar_uc, guardar_uc)
    
    page.title = settings.app_name
    page.window.width = settings.ui.window_width
    page.window.height = settings.ui.window_height
    page.theme_mode = ft.ThemeMode.LIGHT if settings.ui.theme_mode == "light" else ft.ThemeMode.DARK
    page.padding = settings.ui.padding
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)

    # Iniciar la vista
    view = CorrespondenciaView(page, vm)
    page.add(view)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
