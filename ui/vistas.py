import flet as ft
import logging
from typing import Optional
from core.procesador_pdf import ProcesadorPDF
from core.ia_cliente import IACliente
from database.db_manager import save_document

logger = logging.getLogger(__name__)


class VistaCorrespondencia(ft.Column):
    """Vista principal para gestión de correspondencia con IA."""
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        
        # Inicialización de módulos core
        self.procesador = ProcesadorPDF()
        self.ia = IACliente()
        self.ruta_pdf_actual: str = ""
        
        # Configurar FilePicker
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self._on_file_result
        self._page.overlay.append(self.file_picker)

        # --- CAMPOS ADMINISTRATIVOS ---
        self.txt_folio = ft.TextField(
            label="Folio del Documento", 
            hint_text="Ej. OF-2024-001",
            border_color=ft.Colors.OUTLINE,
            width=200
        )
        self.txt_asunto = ft.TextField(
            label="Asunto", 
            hint_text="Breve descripción del tema...",
            border_color=ft.Colors.OUTLINE,
            expand=True
        )

        # --- CAMPOS DE TEXTO PRINCIPALES ---
        self.txt_oficio = ft.TextField(
            label="Contenido del Oficio Original",
            hint_text="El texto aparecerá aquí al cargar un PDF...",
            multiline=True,
            min_lines=12,
            max_lines=20,
            border_color=ft.Colors.OUTLINE,
            expand=True
        )

        self.txt_respuesta = ft.TextField(
            label="Borrador de Contestación (Sugerido por IA)",
            hint_text="La respuesta aparecerá aquí para tu revisión y edición...",
            multiline=True,
            min_lines=12,
            max_lines=20,
            border_color=ft.Colors.BLUE_700,
            expand=True
        )

        self.pr = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_700)

        # --- CONSTRUCCIÓN DE LA INTERFAZ ---
        self.controls = [
            ft.Row([
                ft.Icon(ft.Icons.DESCRIPTION_ROUNDED, color=ft.Colors.BLUE_700, size=30),
                ft.Text("Gestión de Correspondencia e IA", size=24, weight="bold"),
            ]),
            ft.Divider(height=10),
            
            # Fila de Metadatos (Folio y Asunto)
            ft.Row([self.txt_folio, self.txt_asunto]),
            
            ft.Divider(height=10),
            
            # Fila de Botones de Acción
            ft.Row([
                ft.ElevatedButton(
                    "Cargar Oficio PDF",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=self._pick_files_click,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_900)
                ),
                ft.VerticalDivider(width=10),
                ft.FilledButton(
                    "Generar Respuesta con IA",
                    icon=ft.Icons.AUTO_AWESOME,
                    on_click=self._procesar_con_ia,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.AMBER_800)
                ),
                ft.VerticalDivider(width=10),
                ft.ElevatedButton(
                    "Guardar en Archivo",
                    icon=ft.Icons.SAVE,
                    on_click=self._guardar_en_bd,
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700)
                ),
            ]),
            self.pr,
            
            # Área de Trabajo Principal (Textos)
            ft.Row([
                ft.Container(
                    content=self.txt_oficio, 
                    expand=1, 
                    padding=10, 
                    border=ft.border.all(1, ft.Colors.GREY_300), 
                    border_radius=10
                ),
                ft.Container(
                    content=self.txt_respuesta, 
                    expand=1, 
                    padding=10, 
                    border=ft.border.all(1, ft.Colors.BLUE_100), 
                    border_radius=10, 
                    bgcolor=ft.Colors.BLUE_50
                ),
            ], expand=True),
        ]

    # --- MÉTODOS DE EVENTOS ---

    async def _pick_files_click(self, e):
        await self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["pdf"])

    async def _on_file_result(self, e):
        """Maneja el resultado de la selección de archivos."""
        if e.files:
            self.ruta_pdf_actual = e.files[0].path
            self.pr.visible = True
            self._page.update()
            
            try:
                texto = self.procesador.extraer_texto(self.ruta_pdf_actual)
                self.txt_oficio.value = texto
                self._mostrar_notificacion(f"Archivo cargado: {e.files[0].name}", ft.Colors.GREEN)
            except Exception as ex:
                logger.error(f"Error al procesar PDF: {str(ex)}", exc_info=True)
                self._mostrar_notificacion(f"Error al procesar PDF: {str(ex)}", ft.Colors.RED)
            finally:
                self.pr.visible = False
                self._page.update()

    def _procesar_con_ia(self, e):
        if not self.txt_oficio.value or not self.txt_oficio.value.strip():
            self._mostrar_notificacion("Por favor, carga un oficio o escribe el texto primero.", ft.Colors.RED_400)
            return
            
        self.pr.visible = True
        self.txt_respuesta.value = "Conectando con IA... Analizando documento..."
        self._page.update()
        
        try:
            # LLAMADA A LA INTELIGENCIA ARTIFICIAL
            respuesta_generada = self.ia.generar_respuesta(self.txt_oficio.value)
            self.txt_respuesta.value = respuesta_generada
            self._mostrar_notificacion("Borrador generado exitosamente.", ft.Colors.GREEN)
        except Exception as ex:
            logger.error(f"Error al generar respuesta con IA: {str(ex)}", exc_info=True)
            self._mostrar_notificacion(f"Error al generar respuesta: {str(ex)}", ft.Colors.RED)
        finally:
            self.pr.visible = False
            self._page.update()

    def _guardar_en_bd(self, e):
        """Guarda el documento y su respuesta en la base de datos SQLite"""
        if not self.txt_folio.value or not self.txt_folio.value.strip():
            self._mostrar_notificacion("Debes ingresar el Folio para poder guardar.", ft.Colors.RED_400)
            return
        
        if not self.txt_asunto.value or not self.txt_asunto.value.strip():
            self._mostrar_notificacion("Debes ingresar el Asunto para poder guardar.", ft.Colors.RED_400)
            return
            
        if not self.txt_oficio.value or not self.txt_oficio.value.strip():
            self._mostrar_notificacion("No hay contenido de documento para guardar.", ft.Colors.RED_400)
            return

        try:
            save_document(
                folio=self.txt_folio.value.strip(),
                asunto=self.txt_asunto.value.strip(),
                contenido=self.txt_oficio.value, 
                remitente="Pendiente / Extraído",
                ruta=self.ruta_pdf_actual
            )
            self._mostrar_notificacion(
                f"Documento {self.txt_folio.value} guardado en el archivo histórico.", 
                ft.Colors.GREEN_700
            )
        except ValueError as ve:
            logger.warning(f"Error de validación al guardar: {str(ve)}")
            self._mostrar_notificacion(str(ve), ft.Colors.RED_400)
        except Exception as ex:
            logger.error(f"Error al guardar en base de datos: {str(ex)}", exc_info=True)
            self._mostrar_notificacion(f"Error al guardar en base de datos: {str(ex)}", ft.Colors.RED_400)

    def _mostrar_notificacion(self, mensaje: str, color: str):
        """Función auxiliar para mostrar mensajes al usuario de forma limpia"""
        self._page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color
        )
        self._page.snack_bar.open = True
        self._page.update()