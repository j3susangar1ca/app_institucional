import flet as ft
from ui.vistas import VistaCorrespondencia
from database.db_manager import init_db

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

    vista_principal = VistaCorrespondencia(page)
    page.add(vista_principal)
    page.update() # Forzar actualización para registro de controles en overlay

if __name__ == "__main__":
    # CORRECCIÓN: Para Flet 0.8.0+ usamos ft.run(main) para evitar el DeprecationWarning
    ft.run(main)