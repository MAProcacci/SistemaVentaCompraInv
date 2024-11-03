# proveedor.py
import flet as ft
from typing import Callable, List, Tuple
from models import Proveedor
from libreria import BaseApp, get_db_connection, FormField
from libreria import BLUE_COLOR, RED_COLOR, HEADER_SIZE, BUTTON_TEXT_SIZE, COLOR_SNACKBAR
import time

class ProveedorApp(BaseApp):
    """
    Clase que representa la aplicación de Proveedores.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def listar_proveedores(self) -> None:
        """Lista todos los proveedores disponibles en la base de datos."""
        proveedores = self._obtener_proveedores()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Proveedores", size=HEADER_SIZE))

        lista_proveedores = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

        def filtrar_proveedores(e):
            """
            Filtra los proveedores según el valor ingresado en el campo de búsqueda.
            :param e: Evento de cambio de estado.
            :return: None
            """
            filtro = filtro_field.value.lower()
            proveedores_filtrados = [proveedor for proveedor in proveedores if filtro in str(proveedor[0]).lower() or filtro in proveedor[1].lower()]
            actualizar_lista_proveedores(proveedores_filtrados)

        def actualizar_lista_proveedores(proveedores_filtrados):
            """
            Actualiza la lista de proveedores con los proveedores filtrados.
            :param proveedores_filtrados: Lista de proveedores filtrados.
            :return: None
            """
            lista_proveedores.controls.clear()
            for proveedor in proveedores_filtrados:
                lista_proveedores.controls.append(self._crear_boton_proveedor(proveedor))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_proveedores, width=500, border_color=ft.colors.OUTLINE)

        actualizar_lista_proveedores(proveedores)

        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_proveedores,
                expand=True,
                height=400,
                width=500,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            )
        )

        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def _obtener_proveedores(self) -> List[Tuple]:
        """Obtiene la lista de proveedores desde la base de datos.
        :return: Lista de tuplas con los detalles de los proveedores.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores")
            return cursor.fetchall()

    def _crear_boton_proveedor(self, proveedor: Tuple) -> ft.ElevatedButton:
        """Crea un botón con la información del proveedor.
        :param proveedor: Tupla con los detalles del proveedor.
        :return: Botón con la información del proveedor.
        """
        return self._crear_boton_entidad(proveedor, "Proveedor", lambda _: self.consultar_proveedor(proveedor[0]))

    def consultar_proveedor(self, proveedor_id: int) -> None:
        """Consulta los detalles de un proveedor específico.
        :param proveedor_id: ID del proveedor a consultar.
        :return: None
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
        """Obtiene los detalles de un proveedor específico desde la base de datos.
        :param proveedor_id: ID del proveedor a consultar.
        :return: Tupla con los detalles del proveedor.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores WHERE id=?", (proveedor_id,))
            return cursor.fetchone()

    def modificar(self, proveedor: Tuple) -> None:
        """Muestra la interfaz para modificar un proveedor existente.
        :param proveedor: Tupla con los detalles del proveedor a modificar.
        :return: None
        """
        campos = [
            FormField("Nombre", proveedor[1]),
            FormField("Teléfono", proveedor[2]),
            FormField("Email", proveedor[3])
        ]
        self._mostrar_formulario_entidad(proveedor, "Proveedor", campos, self._guardar_proveedor)

    def _guardar_proveedor(self, fields: List[ft.TextField], proveedor: Tuple) -> None:
        """Guarda un proveedor en la base de datos.

        Args:
            fields (List[ft.TextField]): Lista de campos del formulario.
            proveedor (Tuple): Tupla con los detalles del proveedor a modificar.

        :return: None
        """
        nombre, telefono, email = [field.value for field in fields]
        self._validar_campos(fields)
        try:
            nuevo_proveedor = Proveedor(nombre=nombre, telefono=telefono, email=email, id=proveedor[0] if proveedor else None)
            if proveedor:
                nuevo_proveedor.update()
            else:
                nuevo_proveedor.save()
        except ValueError as e:
            self.mostrar_mensaje(f"Error: {str(e)}", RED_COLOR)
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", RED_COLOR)

    def eliminar(self, proveedor_id: int) -> None:
        """Elimina un proveedor de la base de datos.

        Args:
            proveedor_id (int): ID del proveedor a eliminar.

        :return: None
        """
        if self._proveedor_tiene_compras(proveedor_id):
            self.mostrar_mensaje("El proveedor seleccionado tiene compras registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)
            self.main_menu_callback()
        else:
            proveedor = Proveedor(id=proveedor_id, nombre="", telefono="", email="")
            proveedor.delete()
            self.main_menu_callback()

    def _proveedor_tiene_compras(self, proveedor_id: int) -> bool:
        """Verifica si un proveedor tiene compras registradas.

        Args:
            proveedor_id (int): ID del proveedor a verificar.

        Returns:
            bool: True si el proveedor tiene compras registradas, False en caso contrario.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Compras WHERE proveedor_id=?", (proveedor_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo proveedor.

        :return: None
        """
        campos = [
            FormField("Nombre"),
            FormField("Teléfono"),
            FormField("Email")
        ]
        self._mostrar_formulario_entidad(None, "Proveedor", campos, self._guardar_proveedor)

    def main_menu(self) -> None:
        """Muestra el menú principal de gestión de proveedores.

        :return: None
        """
        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Proveedores", size=HEADER_SIZE),
            ft.ElevatedButton("Agregar Proveedor", on_click=lambda _: self.agregar()),
            ft.ElevatedButton("Listar Proveedores", on_click=lambda _: self.listar_proveedores()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def proveedor_app(page: ft.Page, main_menu_callback: Callable[[], None]) -> None:
    """Función principal que inicializa la aplicación de gestión de proveedores.

    Args:
        page (ft.Page): Objeto de la página de la interfaz de usuario.
        main_menu_callback (Callable[[], None]): Función de retorno al menú principal.

    :return: None
    """
    app = ProveedorApp(page, main_menu_callback)
    app.main_menu()

