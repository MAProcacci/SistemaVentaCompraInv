# libreria.py
import flet as ft
from typing import Callable, List, Tuple, Optional, Any
from contextlib import contextmanager
from database import create_connection
import time
from functools import partial
from dataclasses import dataclass

# Constantes
BLUE_COLOR = "blue"
RED_COLOR = "red"
HEADER_SIZE = 24
BUTTON_TEXT_SIZE = 16
COLOR_SNACKBAR = "white"

@contextmanager
def get_db_connection():
    """Administrador de contexto para manejar conexiones a la base de datos."""
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()

@dataclass
class FormField:
    label: str
    value: Optional[str] = None

class BaseApp:
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.main_menu_callback = main_menu_callback

    def mostrar_mensaje(self, mensaje: str, color: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _crear_boton_entidad(self, entidad: Tuple, entidad_name: str, on_click: Callable) -> ft.ElevatedButton:
        """Crea un botón con la información de la entidad."""
        if entidad_name == "Producto":
            return ft.ElevatedButton(
                content=ft.Column(
                    [
                        ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                        ft.Row([ft.Text(f"Stock: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[4]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=on_click,
                data=entidad[0],
                width=500,  # Ajusta este ancho según tus necesidades
            )
        else:
            return ft.ElevatedButton(
                content=ft.Column(
                    [
                        ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                        ft.Row([ft.Text(f"Teléfono: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[2]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=on_click,
                data=entidad[0],
                width=500,  # Ajusta este ancho según tus necesidades
            )

    def _mostrar_formulario_entidad(self, entidad: Tuple = None, entidad_name: str = "Entidad", campos: List[FormField] = [], guardar_callback: Callable = None) -> None:
        """
        Muestra el formulario para agregar o modificar una entidad.

        Args:
            entidad (Tuple, optional): Datos de la entidad a modificar. Si es None, se trata de una nueva entidad.
            entidad_name (str): Nombre de la entidad.
            campos (List[FormField]): Lista de campos del formulario.
            guardar_callback (Callable): Función de devolución de llamada para guardar la entidad.
        """
        fields = [ft.TextField(label=field.label, value=field.value if entidad else "") for field in campos]

        def guardar_entidad(_):
            try:
                if guardar_callback:
                    guardar_callback(fields, entidad)  # Pasar entidad como argumento
                self.main_menu_callback()
            except ValueError as e:
                self.page.add(ft.Text(f"Error: {str(e)}", color=RED_COLOR))
                self.page.update()
            except Exception as e:
                self.mostrar_mensaje(f"Error inesperado: {str(e)}", RED_COLOR)

        self.page.controls.clear()
        self.page.add(
            ft.Text(f"Modificar {entidad_name}" if entidad else f"Agregar {entidad_name}", size=HEADER_SIZE),
            *fields,
            ft.ElevatedButton("Guardar", on_click=guardar_entidad),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _validar_campos(self, campos: List[ft.TextField]) -> None:
        """Valida los campos del formulario."""
        for field in campos:
            if not field.value:
                raise ValueError("Todos los campos son obligatorios")

