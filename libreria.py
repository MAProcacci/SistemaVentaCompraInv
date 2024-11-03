# libreria.py
import flet as ft
from typing import Callable, List, Tuple, Optional, Any
from contextlib import contextmanager
from database import create_connection
import time
from functools import partial
from dataclasses import dataclass
from datetime import datetime

# Constantes
BLUE_COLOR = "blue"
RED_COLOR = "red"
HEADER_SIZE = 24
BUTTON_TEXT_SIZE = 16
COLOR_SNACKBAR = "white"

@contextmanager
def get_db_connection():
    """
    Administrador de contexto para manejar conexiones a la base de datos.

    Yields:
        Connection: Objeto de conexión a la base de datos.
    """
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()

def _crear_menu_fila(text1: str, on_click1: Callable,
                     text2: str, on_click2: Callable) -> ft.Row:
    """Crea una fila de botones de 2 columnaspara el menú en 'Flet'.
    Args:
        text1 (str): Texto del botón 1.
        on_click1 (Callable): Función que se llama cuando se hace click en el botón 1.
        text2 (str): Texto del botón 2.
        on_click2 (Callable): Función que se llama cuando se hace click en el botón 2.
        """
    return ft.Row([
        ft.ElevatedButton(text1, on_click=on_click1),
        ft.Divider(height=20, color="transparent"),
        ft.ElevatedButton(text2, on_click=on_click2),
    ], alignment=ft.MainAxisAlignment.CENTER)

@dataclass
class FormField:
    """
    Clase que representa un campo de formulario.

    Attributes:
        label (str): Etiqueta del campo.
        value (Optional[str]): Valor inicial del campo. Por defecto es None.
    """
    label: str
    value: Optional[str] = None

class BaseApp:
    """
    Clase base para las aplicaciones que utilizan la interfaz de usuario.

    Attributes:
        page (ft.Page): Página de la aplicación.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.main_menu_callback = main_menu_callback

    def _agregar_reporte(self, titulo: str, elementos: List[Any], desde: Optional[str] = None,
                         hasta: Optional[str] = None):
        """
        Agrega un reporte a la página.

        Args:
            titulo (str): Título del reporte.
            elementos (List[Any]): Lista de elementos a mostrar en el reporte.
            desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
            hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        """
        self.page.controls.clear()
        self.page.add(ft.Text(titulo, size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        if desde and hasta:
            self.page.add(ft.Row([
                ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(desde),
                ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(hasta)
            ], alignment=ft.MainAxisAlignment.CENTER))

        column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        list_view = ft.ListView(expand=True, spacing=10, controls=elementos)
        column.controls.append(list_view)
        self.page.add(ft.Container(content=column, expand=True))

        self.page.add(ft.ElevatedButton("Generar CSV", on_click=lambda _: self.generar_csv_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Generar PDF", on_click=lambda _: self.generar_pdf_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def mostrar_mensaje(self, mensaje: str, color: str):
        """
        Muestra un mensaje en la barra de notificaciones.

        Args:
            mensaje (str): Mensaje a mostrar.
            color (str): Color del texto del mensaje.
        """
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _crear_boton_entidad(self, entidad: Tuple, entidad_name: str, on_click: Callable) -> ft.ElevatedButton:
        """
        Crea un botón con la información de la entidad.

        Args:
            entidad (Tuple): Datos de la entidad.
            entidad_name (str): Nombre de la entidad.
            on_click (Callable): Función de devolución de llamada al hacer clic en el botón.

        Returns:
            ft.ElevatedButton: Botón con la información de la entidad.
        """
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
                self.mostrar_mensaje(f"Error: {str(e)}", RED_COLOR)
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
        """
        Valida los campos del formulario.

        Args:
            campos (List[ft.TextField]): Lista de campos del formulario.

        Raises:
            ValueError: Si algún campo está vacío.
        """
        for field in campos:
            if not field.value:
                raise ValueError("Todos los campos son obligatorios")

    def abrir_calendario(self, e, campo_fecha: ft.TextField):
        """
        Abre un calendario para seleccionar una fecha.

        Args:
            e: Evento de Flet.
            campo_fecha (ft.TextField): Campo de texto donde se mostrará la fecha seleccionada.
        """
        date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )

        def on_change(e):
            if date_picker.value:
                campo_fecha.value = date_picker.value.strftime('%Y-%m-%d')
                self.page.update()

        date_picker.on_change = on_change
        self.page.overlay.append(date_picker)
        self.page.update()
        date_picker.open = True
        self.page.update()

    def _validar_fechas(self, desde: str, hasta: str) -> bool:
        """
        Valida que la fecha 'Hasta' no sea menor que la fecha 'Desde'.

        Args:
            desde (str): Fecha de inicio.
            hasta (str): Fecha de fin.

        Returns:
            bool: True si las fechas son válidas, False en caso contrario.
        """
        try:
            desde_date = datetime.strptime(desde, '%Y-%m-%d')
            hasta_date = datetime.strptime(hasta, '%Y-%m-%d')
            if hasta_date < desde_date:
                raise ValueError("La fecha 'Hasta' no puede ser menor que la fecha 'Desde'.")
            return True
        except ValueError as e:
            self.mostrar_mensaje(f"Error: {str(e)}")
            return False

