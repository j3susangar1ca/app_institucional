import flet as ft
from src.presentation.flet.viewmodels.correspondencia_viewmodel import CorrespondenciaViewModel

class CorrespondenciaView(ft.Column):
    """Vista de correspondencia refactorizada para Clean Architecture."""
    
    def __init__(self, page: ft.Page, view_model: CorrespondenciaViewModel):
        super().__init__()
        self._page = page
        self.vm = view_model
        
        # Vincular callbacks del ViewModel
        self.vm.on_state_changed = self._render
        self.vm.on_notification = self._show_snack

        # FilePicker
        self.file_picker = ft.FilePicker()
        self.file_picker.on_result = self._on_file_result
        self._page.overlay.append(self.file_picker)

        # Controles
        self.txt_folio = ft.TextField(
            label="Folio", width=200, 
            on_change=lambda e: self.vm.set_folio(e.data)
        )
        self.txt_asunto = ft.TextField(
            label="Asunto", expand=True,
            on_change=lambda e: self.vm.set_asunto(e.data)
        )
        self.txt_oficio = ft.TextField(
            label="Contenido", multiline=True, min_lines=10, expand=True,
            on_change=lambda e: self.vm.set_contenido(e.data)
        )
        self.txt_respuesta = ft.TextField(
            label="Respuesta IA", multiline=True, min_lines=10, expand=True,
            on_change=lambda e: self.vm.set_respuesta(e.data)
        )
        self.pr = ft.ProgressBar(visible=False)

        self.controls = [
            ft.Text("Gestión de Correspondencia", size=24, weight="bold"),
            ft.Row([self.txt_folio, self.txt_asunto]),
            ft.Row([
                ft.ElevatedButton("Cargar PDF", icon=ft.Icons.UPLOAD_FILE, on_click=self._on_pick_click),
                ft.FilledButton("Generar IA", icon=ft.Icons.AUTO_AWESOME, on_click=lambda _: self.vm.generar_respuesta()),
                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda _: self.vm.guardar()),
            ]),
            self.pr,
            ft.Row([self.txt_oficio, self.txt_respuesta], expand=True),
        ]

    def _render(self):
        """Actualiza la UI con el estado del ViewModel."""
        self.txt_folio.value = self.vm.folio
        self.txt_asunto.value = self.vm.asunto
        self.txt_oficio.value = self.vm.contenido
        self.txt_respuesta.value = self.vm.respuesta
        self.pr.visible = self.vm.is_loading
        self._page.update()

    def _show_snack(self, message: str, color: str):
        self._page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self._page.snack_bar.open = True
        self._page.update()

    def _on_pick_click(self, e):
        # NOTA: En Flet 0.80.1 pick_files es asíncrono en algunos contextos, 
        # pero aquí lo llamamos de forma segura.
        self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["pdf"])

    def _on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.vm.select_file(e.files[0].path)
