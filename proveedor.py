# proveedor.py
import flet as ft
from typing import Callable, List, Tuple
from contextlib import contextmanager
from models import Proveedor
from database import create_connection
import time

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

class ProveedorApp:
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        """
        Constructor de la clase ProveedorApp.

        Args:
            page (ft.Page): La página principal de la aplicación.
            main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
        """
        self.page = page
        self.main_menu_callback = main_menu_callback

    def listar_proveedores(self) -> None:
        """Lista todos los proveedores disponibles en la base de datos."""
        proveedores = self._obtener_proveedores()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Proveedores", size=HEADER_SIZE))

        # Crear un contenedor scrollable para la lista de proveedores
        lista_proveedores = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )

        def filtrar_proveedores(e):
            filtro = filtro_field.value.lower()
            proveedores_filtrados = [proveedor for proveedor in proveedores if filtro in str(proveedor[0]).lower() or filtro in proveedor[1].lower()]
            actualizar_lista_proveedores(proveedores_filtrados)

        def actualizar_lista_proveedores(proveedores_filtrados):
            lista_proveedores.controls.clear()
            for proveedor in proveedores_filtrados:
                lista_proveedores.controls.append(self._crear_boton_proveedor(proveedor))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_proveedores)

        # Inicialmente, mostrar todos los proveedores
        actualizar_lista_proveedores(proveedores)

        # Agregar el contenedor scrollable a la página
        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_proveedores,
                expand=True,
                height=400,  # Ajusta esta altura según tus necesidades
                width=500,  # Ajusta esta anchura según tus necesidades
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            )
        )

        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def _obtener_proveedores(self) -> List[Tuple]:
        """Obtiene la lista de proveedores desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores")
            return cursor.fetchall()

    def _crear_boton_proveedor(self, proveedor: Tuple) -> ft.ElevatedButton:
        """Crea un botón con la información del proveedor."""
        return ft.ElevatedButton(
            content=ft.Column(
                [
                    ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                            ft.Text(f"{proveedor[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ft.Row([ft.Text(f"Teléfono: ", color=BLUE_COLOR),
                            ft.Text(f"{proveedor[2]}", weight=ft.FontWeight.BOLD, color="white")]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            on_click=lambda _: self.consultar_proveedor(proveedor[0]),
            data=proveedor[0],
            width=500,  # Ajusta este ancho según tus necesidades
        )

    def consultar_proveedor(self, proveedor_id: int) -> None:
        """
        Consulta los detalles de un proveedor específico.

        Args:
            proveedor_id (int): ID del proveedor a consultar.
        """
        proveedor = self._obtener_proveedor(proveedor_id)
        self.page.controls.clear()
        self.page.add(
            ft.Text("Detalles del Proveedor", size=HEADER_SIZE),
            ft.Row(
                [
                    ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{proveedor[1]}"),
                    ft.Text("Teléfono:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{proveedor[2]}"),
                    ft.Text("Email:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{proveedor[3]}", size=BUTTON_TEXT_SIZE),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.ElevatedButton("Modificar", on_click=lambda _: self.modificar(proveedor)),
            ft.ElevatedButton("Eliminar", on_click=lambda _: self.eliminar(proveedor_id)),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def _obtener_proveedor(self, proveedor_id: int) -> Tuple:
        """Obtiene los detalles de un proveedor específico desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores WHERE id=?", (proveedor_id,))
            return cursor.fetchone()

    def _mostrar_formulario_proveedor(self, proveedor: Tuple = None) -> None:
        """
        Muestra el formulario para agregar o modificar un proveedor.

        Args:
            proveedor (Tuple, optional): Datos del proveedor a modificar. Si es None, se trata de un nuevo proveedor.
        """
        nombre_field = ft.TextField(label="Nombre", value=proveedor[1] if proveedor else "")
        telefono_field = ft.TextField(label="Teléfono", value=proveedor[2] if proveedor else "")
        email_field = ft.TextField(label="Email", value=proveedor[3] if proveedor else "")

        def guardar_proveedor(_):
            try:
                self._validar_campos(nombre_field.value, telefono_field.value, email_field.value)
                nuevo_proveedor = Proveedor(
                    nombre=nombre_field.value,
                    telefono=telefono_field.value,
                    email=email_field.value,
                    id=proveedor[0] if proveedor else None
                )
                if proveedor:
                    nuevo_proveedor.update()
                else:
                    nuevo_proveedor.save()
                self.main_menu_callback()
            except ValueError as e:
                self.page.add(ft.Text(f"Error: {str(e)}", color=RED_COLOR))
                self.page.update()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Modificar Proveedor" if proveedor else "Agregar Proveedor", size=HEADER_SIZE),
            nombre_field,
            telefono_field,
            email_field,
            ft.ElevatedButton("Guardar", on_click=guardar_proveedor),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _validar_campos(self, nombre: str, telefono: str, email: str) -> None:
        """Valida los campos del formulario de proveedor."""
        if not nombre or not telefono or not email:
            raise ValueError("Todos los campos son obligatorios")
        if not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        if '@' not in email:
            raise ValueError("El email debe ser válido")

    def modificar(self, proveedor: Tuple) -> None:
        """
        Muestra la interfaz para modificar un proveedor existente.

        Args:
            proveedor (Tuple): Tupla que contiene los detalles del proveedor.
        """
        self._mostrar_formulario_proveedor(proveedor)

    def mostrar_mensaje(self, mensaje: str, color: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def eliminar(self, proveedor_id: int) -> None:
        """
        Elimina un proveedor de la base de datos.

        Args:
            proveedor_id (int): ID del proveedor a eliminar.
        """
        if self._proveedor_tiene_compras(proveedor_id):
            self.mostrar_mensaje("El proveedor seleccionado tiene compras registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)  # Esperar 2 segundos antes de volver al menú principal
            self.main_menu_callback()
        else:
            proveedor = Proveedor(id=proveedor_id, nombre="", telefono="", email="")
            proveedor.delete()
            self.main_menu_callback()

    def _proveedor_tiene_compras(self, proveedor_id: int) -> bool:
        """
        Verifica si un proveedor tiene compras registradas.

        Args:
            proveedor_id (int): ID del proveedor a verificar.

        Returns:
            bool: True si el proveedor tiene compras, False en caso contrario.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Compras WHERE proveedor_id=?", (proveedor_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo proveedor."""
        self._mostrar_formulario_proveedor()

    def main_menu(self) -> None:
        """Muestra el menú principal de gestión de proveedores."""
        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Proveedores", size=HEADER_SIZE),
            ft.ElevatedButton("Agregar Proveedor", on_click=lambda _: self.agregar()),
            ft.ElevatedButton("Listar Proveedores", on_click=lambda _: self.listar_proveedores()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def proveedor_app(page: ft.Page, main_menu_callback: Callable[[], None]) -> None:
    """
    Función principal que inicializa la aplicación de gestión de proveedores.

    Args:
        page (ft.Page): La página principal de la aplicación.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
    """
    app = ProveedorApp(page, main_menu_callback)
    app.main_menu()
