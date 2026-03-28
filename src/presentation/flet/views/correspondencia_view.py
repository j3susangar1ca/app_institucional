"""
Vista principal de correspondencia.
Implementa la UI siguiendo el patrón MVVM.
"""
import flet as ft
import logging
from src.presentation.flet.viewmodels.correspondencia_vm import (
    CorrespondenciaViewModel,
    CorrespondenciaState,
    EstadoVista,
)

logger = logging.getLogger(__name__)

class CorrespondenciaView(ft.Column):
    """
    Vista principal para gestión de correspondencia.
    """
    
    def __init__(self, page: ft.Page, viewmodel: CorrespondenciaViewModel):
        super().__init__()
        self._page = page
        self._vm = viewmodel
        self._vm.set_on_state_change(self._on_state_change)
        self._init_ui()
        self._render_state(self._vm.state)
    
    def _init_ui(self) -> None:
        # File Picker
        self._file_picker = ft.FilePicker()
        self._file_picker.on_result = self._on_file_result
        self._page.overlay.append(self._file_picker)
        
        # Campos
        self._txt_folio = ft.TextField(
            label="Folio", width=200, on_change=self._on_folio_change,
            input_filter=ft.InputFilter(regex_string=r"[A-Z0-9\-]", allow=True)
        )
        self._txt_asunto = ft.TextField(label="Asunto", expand=True, on_change=self._on_asunto_change)
        self._txt_oficio = ft.TextField(
            label="Contenido Oficio", multiline=True, min_lines=12, max_lines=20,
            expand=True, on_change=self._on_contenido_change
        )
        self._txt_respuesta = ft.TextField(
            label="Respuesta IA", multiline=True, min_lines=12, max_lines=20,
            expand=True, bgcolor=ft.Colors.BLUE_50
        )
        
        self._progress_bar = ft.ProgressBar(visible=False, color=ft.Colors.BLUE_700)
        self._status_text = ft.Text(value="", size=12)
        
        # Botones
        self._btn_cargar = ft.ElevatedButton("Cargar PDF", icon=ft.Icons.UPLOAD_FILE, on_click=self._on_cargar_click)
        self._btn_generar = ft.FilledButton("Generar con IA", icon=ft.Icons.AUTO_AWESOME, on_click=self._on_generar_click)
        self._btn_guardar = ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=self._on_guardar_click)
        self._btn_limpiar = ft.OutlinedButton("Limpiar", icon=ft.Icons.CLEAR_ALL, on_click=self._on_limpiar_click)
        
        self.controls = [
            ft.Row([ft.Icon(ft.Icons.DESCRIPTION), ft.Text("Gestión de Correspondencia e IA", size=24, weight="bold")]),
            ft.Divider(),
            ft.Row([self._txt_folio, self._txt_asunto]),
            ft.Row([self._btn_cargar, self._btn_generar, self._btn_guardar, self._btn_limpiar]),
            ft.Column([self._progress_bar, self._status_text]),
            ft.Row([
                ft.Container(self._txt_oficio, expand=1, padding=10, border=ft.border.all(1, ft.Colors.GREY_300), border_radius=10),
                ft.Container(self._txt_respuesta, expand=1, padding=10, border=ft.border.all(1, ft.Colors.BLUE_100), border_radius=10),
            ], expand=True),
        ]

    def _on_state_change(self, state: CorrespondenciaState) -> None:
        self._render_state(state)
        self._page.update()

    def _render_state(self, state: CorrespondenciaState) -> None:
        self._txt_folio.value = state.folio
        self._txt_asunto.value = state.asunto
        self._txt_oficio.value = state.contenido_oficio
        self._txt_respuesta.value = state.contenido_respuesta
        
        self._progress_bar.visible = state.estado in [
            EstadoVista.CARGANDO, EstadoVista.PROCESANDO_PDF, 
            EstadoVista.GENERANDO_RESPUESTA, EstadoVista.GUARDANDO
        ]
        
        self._status_text.value = state.mensaje or state.mensaje_error
        self._status_text.color = ft.Colors.RED if state.estado == EstadoVista.ERROR else ft.Colors.GREY_700
        
        if state.estado == EstadoVista.ERROR:
            self._mostrar_snackbar(state.mensaje_error, ft.Colors.RED)
        elif state.estado == EstadoVista.EXITO and state.mensaje:
            self._mostrar_snackbar(state.mensaje, ft.Colors.GREEN)

    def _mostrar_snackbar(self, msg, color):
        self._page.snack_bar = ft.SnackBar(content=ft.Text(msg), bgcolor=color)
        self._page.snack_bar.open = True

    def _on_folio_change(self, e): self._vm.actualizar_folio(e.control.value)
    def _on_asunto_change(self, e): self._vm.actualizar_asunto(e.control.value)
    def _on_contenido_change(self, e): self._vm.actualizar_contenido_oficio(e.control.value)
    def _on_cargar_click(self, e): self._file_picker.pick_files(allowed_extensions=["pdf"])
    async def _on_file_result(self, e):
        if e.files: self._vm.procesar_pdf(e.files[0].path)
    def _on_generar_click(self, e): self._vm.generar_respuesta()
    def _on_guardar_click(self, e): self._vm.guardar_documento()
    def _on_limpiar_click(self, e): self._vm.limpiar_estado()
