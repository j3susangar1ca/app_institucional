import sys
import os

# Añadir 'src' al path para que los imports internos funcionen
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.main import main
import flet as ft

if __name__ == "__main__":
    # Redirigir a la ejecución en src/main.py
    ft.app(target=main)
