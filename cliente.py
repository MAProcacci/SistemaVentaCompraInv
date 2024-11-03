# cliente.py
import flet as ft
from typing import Callable, List, Tuple
from models import Cliente
from libreria import BaseApp, get_db_connection, FormField
from libreria import BLUE_COLOR, RED_COLOR, HEADER_SIZE, BUTTON_TEXT_SIZE, COLOR_SNACKBAR
import time

class ClienteApp(BaseApp):
    """
    Clase que representa la interfaz de usuario para administrar clientes.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def listar_clientes(self) -> None:
        """Lista todos los clientes disponibles en la base de datos."""
        clientes = self._obtener_clientes()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Clientes", size=HEADER_SIZE))

        lista_clientes = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

        def filtrar_clientes(e):
            """
            Filtra los clientes según el filtro introducido por el usuario.
            """
            filtro = filtro_field.value.lower()
            clientes_filtrados = [cliente for cliente in clientes if filtro in str(cliente[0]).lower() or filtro in cliente[1].lower()]
            actualizar_lista_clientes(clientes_filtrados)

        def actualizar_lista_clientes(clientes_filtrados):
            """
            Actualiza la lista de clientes mostrando los clientes filtrados.
            Args:
                clientes_filtrados (List[Tuple]): Lista de clientes filtrados.
            """
            lista_clientes.controls.clear()
            for cliente in clientes_filtrados:
                lista_clientes.controls.append(self._crear_boton_cliente(cliente))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_clientes, width=500, border_color=ft.colors.OUTLINE)

        actualizar_lista_clientes(clientes)

        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_clientes,
                expand=True,
                height=400,
                width=500,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            )
        )

        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def _obtener_clientes(self) -> List[Tuple]:
        """Obtiene la lista de clientes desde la base de datos.
        Returns:
            List[Tuple]: Lista de tuplas con los detalles de los clientes.
            """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes")
            return cursor.fetchall()

    def _crear_boton_cliente(self, cliente: Tuple) -> ft.ElevatedButton:
        """Crea un botón con la información del cliente.
        Args:
            cliente (Tuple): Tupla con los detalles del cliente.
        Returns:
            ft.ElevatedButton: Botón con la información del cliente.
            """
        return self._crear_boton_entidad(cliente, "Cliente", lambda _: self.consultar_cliente(cliente[0]))

    def consultar_cliente(self, cliente_id: int) -> None:
        """Consulta los detalles de un cliente específico.
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
        """Obtiene los detalles de un cliente específico desde la base de datos.
         Args:
            cliente_id (int): ID del cliente a consultar.
         Returns:
            Tuple: Tupla con los detalles del cliente.
            """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes WHERE id=?", (cliente_id,))
            return cursor.fetchone()

    def modificar(self, cliente: Tuple) -> None:
        """Muestra la interfaz para modificar un cliente existente.
        Args:
            cliente (Tuple): Tupla con los detalles del cliente.
            """
        campos = [FormField("Nombre", cliente[1]), FormField("Teléfono", cliente[2]), FormField("Email", cliente[3])]
        self._mostrar_formulario_entidad(cliente, "Cliente", campos, self._guardar_cliente)

    def _guardar_cliente(self, fields: List[ft.TextField], cliente: Tuple) -> None:
        """Guarda un cliente en la base de datos.
        Args:
            fields (List[ft.TextField]): Lista de campos del formulario.
            cliente (Tuple): Tupla con los detalles del cliente.
            """
        nombre, telefono, email = [field.value for field in fields]
        self._validar_campos(fields)
        nuevo_cliente = Cliente(nombre=nombre, telefono=telefono, email=email, id=cliente[0] if cliente else None)
        if cliente:
            nuevo_cliente.update()
        else:
            nuevo_cliente.save()

    def eliminar(self, cliente_id: int) -> None:
        """Elimina un cliente de la base de datos.
        Args:
            cliente_id (int): ID del cliente a eliminar.
            """
        if self._cliente_tiene_ventas(cliente_id):
            self.mostrar_mensaje("El cliente seleccionado tiene ventas registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)
            self.main_menu_callback()
        else:
            cliente = Cliente(id=cliente_id, nombre="", telefono="", email="")
            cliente.delete()
            self.main_menu_callback()

    def _cliente_tiene_ventas(self, cliente_id: int) -> bool:
        """Verifica si un cliente tiene ventas registradas.
        Args:
            cliente_id (int): ID del cliente a verificar.
        Returns:
            bool: True si el cliente tiene ventas registradas, False en caso contrario.
            """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Ventas WHERE cliente_id=?", (cliente_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo cliente."""
        campos = [FormField("Nombre"), FormField("Teléfono"), FormField("Email")]
        self._mostrar_formulario_entidad(None, "Cliente", campos, self._guardar_cliente)

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
    """Función principal que inicializa la aplicación de gestión de clientes.
    Args:
        page (ft.Page): Objeto de la página de la interfaz de usuario.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
        """
    app = ClienteApp(page, main_menu_callback)
    app.main_menu()
