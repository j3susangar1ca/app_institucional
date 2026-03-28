import flet as ft

def custom_button(text, on_click):
    return ft.ElevatedButton(text=text, on_click=on_click)

def doc_card(title, subtitle):
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        title=ft.Text(title),
                        subtitle=ft.Text(subtitle),
                    ),
                ]
            ),
            padding=10,
        )
    )
