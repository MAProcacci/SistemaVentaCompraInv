# producto.py
import flet as ft
from typing import Callable, List, Tuple
from models import Producto
from libreria import BaseApp, get_db_connection, FormField
from libreria import BLUE_COLOR, RED_COLOR, HEADER_SIZE, BUTTON_TEXT_SIZE, COLOR_SNACKBAR
import time

class ProductoApp(BaseApp):
    """
    Clase que representa la app para administrar productos.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def listar_productos(self) -> None:
        """Lista todos los productos disponibles en la base de datos."""
        productos = self._obtener_productos()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Productos", size=HEADER_SIZE))

        lista_productos = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

        def filtrar_productos(e):
            """
            Filtra los productos según el filtro ingresado.
            """
            filtro = filtro_field.value.lower()
            productos_filtrados = [producto for producto in productos if filtro in str(producto[0]).lower() or filtro in producto[1].lower()]
            actualizar_lista_productos(productos_filtrados)

        def actualizar_lista_productos(productos_filtrados):
            """
            Actualiza la lista de productos en la interfaz gráfica.
             :param productos_filtrados: Lista de productos filtrados.
             """
            lista_productos.controls.clear()
            for producto in productos_filtrados:
                lista_productos.controls.append(self._crear_boton_producto(producto))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_productos, width=500, border_color=ft.colors.OUTLINE)

        actualizar_lista_productos(productos)

        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_productos,
                expand=True,
                height=400,
                width=500,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            )
        )

        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def _obtener_productos(self) -> List[Tuple]:
        """Obtiene la lista de productos desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Productos")
            return cursor.fetchall()

    def _crear_boton_producto(self, producto: Tuple) -> ft.ElevatedButton:
        """Crea un botón con la información del producto.
         :param producto: Tupla con los datos del producto (id, nombre, descripcion, precio, stock).
         :return: Botón con la información del producto.
         """
        return self._crear_boton_entidad(producto, "Producto", lambda _: self.consultar_producto(producto[0]))

    def consultar_producto(self, producto_id: int) -> None:
        """Consulta los detalles de un producto específico.
         :param producto_id: ID del producto a consultar.
         """
        producto = self._obtener_producto(producto_id)
        self.page.controls.clear()
        self.page.add(
            ft.Text("Detalles del Producto", size=HEADER_SIZE),
            ft.Row(
                [
                    ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{producto[1]}"),
                    ft.Text("Descripción:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{producto[2]}"),
                    ft.Text("Precio:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"${producto[3]:.2f}", size=BUTTON_TEXT_SIZE),
                    ft.Text("Stock:", weight=ft.FontWeight.BOLD, color=BLUE_COLOR),
                    ft.Text(f"{producto[4]}", size=BUTTON_TEXT_SIZE),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            ft.ElevatedButton("Modificar", on_click=lambda _: self.modificar(producto)),
            ft.ElevatedButton("Eliminar", on_click=lambda _: self.eliminar(producto_id)),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def _obtener_producto(self, producto_id: int) -> Tuple:
        """Obtiene los detalles de un producto específico desde la base de datos.
         :param producto_id: ID del producto a consultar.
         :return: Tupla con los datos del producto (id, nombre, descripcion, precio, stock).
         """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Productos WHERE id=?", (producto_id,))
            return cursor.fetchone()

    def modificar(self, producto: Tuple) -> None:
        """Muestra la interfaz para modificar un producto existente.
         :param producto: Tupla con los datos del producto (id, nombre, descripcion, precio, stock).
         """
        campos = [
            FormField("Nombre", producto[1]),
            FormField("Descripción", producto[2]),
            FormField("Precio", str(producto[3])),
            FormField("Stock", str(producto[4]))
        ]
        self._mostrar_formulario_entidad(producto, "Producto", campos, self._guardar_producto)

    def _guardar_producto(self, fields: List[ft.TextField], producto: Tuple) -> None:
        """Guarda un producto en la base de datos.
         :param fields: Lista de campos del formulario.
         :param producto: Tupla con los datos del producto a modificar (id, nombre, descripcion, precio, stock).
         """
        nombre, descripcion, precio, stock = [field.value for field in fields]
        self._validar_campos(fields)
        try:
            nuevo_producto = Producto(nombre=nombre, descripcion=descripcion, precio=float(precio), stock=int(stock), id=producto[0] if producto else None)
            if producto:
                nuevo_producto.update()
            else:
                nuevo_producto.save()
        except ValueError as e:
            self.mostrar_mensaje(f"Error: {str(e)}", RED_COLOR)
        except Exception as e:
            self.mostrar_mensaje(f"Error inesperado: {str(e)}", RED_COLOR)

    def eliminar(self, producto_id: int) -> None:
        """Elimina un producto de la base de datos.
         :param producto_id: ID del producto a eliminar.
         """
        if self._producto_tiene_ventas(producto_id):
            self.mostrar_mensaje("El producto seleccionado tiene ventas registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)
            self.main_menu_callback()
        else:
            producto = Producto(id=producto_id, nombre="", descripcion="", precio=0, stock=0)
            producto.delete()
            self.main_menu_callback()

    def _producto_tiene_ventas(self, producto_id: int) -> bool:
        """Verifica si un producto tiene ventas registradas.
         :param producto_id: ID del producto a verificar.
         :return: True si el producto tiene ventas, False si no."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Ventas WHERE producto_id=?", (producto_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo producto."""
        campos = [
            FormField("Nombre"),
            FormField("Descripción"),
            FormField("Precio"),
            FormField("Stock")
        ]
        self._mostrar_formulario_entidad(None, "Producto", campos, self._guardar_producto)

    def main_menu(self) -> None:
        """Muestra el menú principal de gestión de productos."""
        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Productos", size=HEADER_SIZE),
            ft.ElevatedButton("Agregar Producto", on_click=lambda _: self.agregar()),
            ft.ElevatedButton("Listar Productos", on_click=lambda _: self.listar_productos()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def producto_app(page: ft.Page, main_menu_callback: Callable[[], None]) -> None:
    """Función principal que inicializa la aplicación de gestión de productos.
     Args:
         page (ft.Page): La página principal de la aplicación.
         main_menu_callback (Callable[[], None]): Callback para volver al menú principal.
         """
    app = ProductoApp(page, main_menu_callback)
    app.main_menu()

