import flet as ft
from ui.vistas import VistaCorrespondencia
from database.db_manager import init_db
import logging

# Configurar logging para ver mensajes de error reales
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    try:
        # 1. Inicializar la base de datos local
        init_db()
        
        # 2. Configuración de la ventana
        page.title = "Sistema de Archivo e IA"
        page.window.width = 1100
        page.window.height = 800
        page.window.resizable = True
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 30
        page.bgcolor = ft.Colors.BLUE_GREY_50
        page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE_900)
        
        # 3. Manejador de errores de la página
        def on_error(e):
            logger.error(f"Error en la página: {e}")
            
        page.on_error = on_error
        
        # 4. Cargar vista principal
        vista_principal = VistaCorrespondencia(page)
        page.add(vista_principal)
        page.update()
        
    except Exception as e:
        logger.error(f"Error fatal al inicializar: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    # Configuración para Linux con fallback automático
    import os
    import sys
    
    # Variables de entorno para reducir errores gráficos en Linux
    os.environ.setdefault("GDK_BACKEND", "x11")
    
    try:
        # Intentar modo desktop primero
        ft.app(target=main, view=ft.AppView.FLET_APP, port=8550)
    except Exception as e:
        logger.warning(f"Modo desktop falló ({e}), usando modo web...")
        # Fallback a modo web
        print(f"\n{'='*60}")
        print(f"Iniciando en modo web: http://localhost:8550")
        print(f"{'='*60}\n")
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)