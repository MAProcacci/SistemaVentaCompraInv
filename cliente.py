# cliente.py
import flet as ft
from typing import Callable, List, Tuple
from contextlib import contextmanager
from models import Cliente
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

class ClienteApp:
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        """
        Constructor de la clase ClienteApp.

        Args:
            page (ft.Page): La página principal de la aplicación.
            main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
        """
        self.page = page
        self.main_menu_callback = main_menu_callback

    def listar_clientes(self) -> None:
        """Lista todos los clientes disponibles en la base de datos."""
        clientes = self._obtener_clientes()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Clientes", size=HEADER_SIZE))

        # Crear un contenedor scrollable para la lista de clientes
        lista_clientes = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )

        def filtrar_clientes(e):
            filtro = filtro_field.value.lower()
            clientes_filtrados = [cliente for cliente in clientes if filtro in str(cliente[0]).lower() or filtro in cliente[1].lower()]
            actualizar_lista_clientes(clientes_filtrados)

        def actualizar_lista_clientes(clientes_filtrados):
            lista_clientes.controls.clear()
            for cliente in clientes_filtrados:
                lista_clientes.controls.append(self._crear_boton_cliente(cliente))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre",
                                    on_change=filtrar_clientes,
                                    width=500,
                                    border_color=ft.colors.OUTLINE)

        # Inicialmente, mostrar todos los clientes
        actualizar_lista_clientes(clientes)

        # Agregar el contenedor scrollable a la página
        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_clientes,
                expand=True,
                height=400,  # Ajusta esta altura según tus necesidades
                width=500,  # Ajusta este ancho aquí dependiendo de tus necesidades
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            )
        )

        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def _obtener_clientes(self) -> List[Tuple]:
        """Obtiene la lista de clientes desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes")
            return cursor.fetchall()

    def _crear_boton_cliente(self, cliente: Tuple) -> ft.ElevatedButton:
        """Crea un botón con la información del cliente."""
        return ft.ElevatedButton(
            content=ft.Column(
                [
                    ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                            ft.Text(f"{cliente[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ft.Row([ft.Text(f"Teléfono: ", color=BLUE_COLOR),
                            ft.Text(f"{cliente[2]}", weight=ft.FontWeight.BOLD, color="white")]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            on_click=lambda _: self.consultar_cliente(cliente[0]),
            data=cliente[0],
            width=500,  # Ajusta este ancho según tus necesidades
        )

    def consultar_cliente(self, cliente_id: int) -> None:
        """
        Consulta los detalles de un cliente específico.

        Args:
            cliente_id (int): ID del cliente a consultar.
        """
        cliente = self._obtener_cliente(cliente_id)
        self.page.controls.clear()
        self.page.add(
            ft.Text("Detalles del Cliente", size=HEADER_SIZE),
            ft.Row(
                [
                    ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{cliente[1]}"),
                    ft.Text("Teléfono:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{cliente[2]}"),
                    ft.Text("Email:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{cliente[3]}", size=BUTTON_TEXT_SIZE),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.ElevatedButton("Modificar", on_click=lambda _: self.modificar(cliente)),
            ft.ElevatedButton("Eliminar", on_click=lambda _: self.eliminar(cliente_id)),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def _obtener_cliente(self, cliente_id: int) -> Tuple:
        """Obtiene los detalles de un cliente específico desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes WHERE id=?", (cliente_id,))
            return cursor.fetchone()

    def _mostrar_formulario_cliente(self, cliente: Tuple = None) -> None:
        """
        Muestra el formulario para agregar o modificar un cliente.

        Args:
            cliente (Tuple, optional): Datos del cliente a modificar. Si es None, se trata de un nuevo cliente.
        """
        nombre_field = ft.TextField(label="Nombre", value=cliente[1] if cliente else "")
        telefono_field = ft.TextField(label="Teléfono", value=cliente[2] if cliente else "")
        email_field = ft.TextField(label="Email", value=cliente[3] if cliente else "")

        def guardar_cliente(_):
            try:
                self._validar_campos(nombre_field.value, telefono_field.value, email_field.value)
                nuevo_cliente = Cliente(
                    nombre=nombre_field.value,
                    telefono=telefono_field.value,
                    email=email_field.value,
                    id=cliente[0] if cliente else None
                )
                if cliente:
                    nuevo_cliente.update()
                else:
                    nuevo_cliente.save()
                self.main_menu_callback()
            except ValueError as e:
                self.page.add(ft.Text(f"Error: {str(e)}", color=RED_COLOR))
                self.page.update()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Modificar Cliente" if cliente else "Agregar Cliente", size=HEADER_SIZE),
            nombre_field,
            telefono_field,
            email_field,
            ft.ElevatedButton("Guardar", on_click=guardar_cliente),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _validar_campos(self, nombre: str, telefono: str, email: str) -> None:
        """Valida los campos del formulario de cliente."""
        if not nombre or not telefono or not email:
            raise ValueError("Todos los campos son obligatorios")
        if not telefono.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        if '@' not in email:
            raise ValueError("El email debe ser válido")

    def modificar(self, cliente: Tuple) -> None:
        """
        Muestra la interfaz para modificar un cliente existente.

        Args:
            cliente (Tuple): Tupla que contiene los detalles del cliente.
        """
        self._mostrar_formulario_cliente(cliente)

    def mostrar_mensaje(self, mensaje: str, color: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def eliminar(self, cliente_id: int) -> None:
        """
        Elimina un cliente de la base de datos.

        Args:
            cliente_id (int): ID del cliente a eliminar.
        """
        if self._cliente_tiene_ventas(cliente_id):
            self.mostrar_mensaje("El cliente seleccionado tiene ventas registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)  # Esperar 2 segundos antes de volver al menú principal
            self.main_menu_callback()
        else:
            cliente = Cliente(id=cliente_id, nombre="", telefono="", email="")
            cliente.delete()
            self.main_menu_callback()

    def _cliente_tiene_ventas(self, cliente_id: int) -> bool:
        """
        Verifica si un cliente tiene ventas registradas.

        Args:
            cliente_id (int): ID del cliente a verificar.

        Returns:
            bool: True si el cliente tiene ventas, False en caso contrario.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Ventas WHERE cliente_id=?", (cliente_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo cliente."""
        self._mostrar_formulario_cliente()

    def main_menu(self) -> None:
        """Muestra el menú principal de gestión de clientes."""
        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Clientes", size=HEADER_SIZE),
            ft.ElevatedButton("Agregar Cliente", on_click=lambda _: self.agregar()),
            ft.ElevatedButton("Listar Clientes", on_click=lambda _: self.listar_clientes()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def cliente_app(page: ft.Page, main_menu_callback: Callable[[], None]) -> None:
    """
    Función principal que inicializa la aplicación de gestión de clientes.

    Args:
        page (ft.Page): La página principal de la aplicación.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
    """
    app = ClienteApp(page, main_menu_callback)
    app.main_menu()
