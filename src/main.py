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

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
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
    
    page.title = "Sistema de Archivo e IA"
    page.window.width = 1100
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)

    # Iniciar la vista
    view = CorrespondenciaView(page, vm)
    page.add(view)
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
