import flet as ft
from ui.vistas import VistaCorrespondencia
from database.db_manager import init_db
import logging

# Configurar logging para ver mensajes de error reales
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    # 1. Inicializar la base de datos local
    init_db()
    
    # 2. Configuración de la ventana
    page.title = "Sistema de Archivo e IA"
    page.window.width = 1100
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30
    page.bgcolor = ft.Colors.BLUE_GREY_50
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)

    # 3. Cargar vista principal
    vista_principal = VistaCorrespondencia(page)
    page.add(vista_principal)
    # ELIMINA el page.update() de aquí, ya lo pusimos en vistas.py

if __name__ == "__main__":
    # En Flet 0.21+ esto no es necesario, puedes usar ft.app(main) 
    ft.run(main)