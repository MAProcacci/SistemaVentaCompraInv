# producto.py
import flet as ft
from typing import Callable, List, Tuple
from contextlib import contextmanager
from models import Producto
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

class ProductoApp:
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        """
        Constructor de la clase ProductoApp.

        Args:
            page (ft.Page): La página principal de la aplicación.
            main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
        """
        self.page = page
        self.main_menu_callback = main_menu_callback

    def listar_productos(self) -> None:
        """Lista todos los productos disponibles en la base de datos."""
        productos = self._obtener_productos()
        self.page.controls.clear()
        self.page.add(ft.Text("Listado de Productos", size=HEADER_SIZE))

        # Crear un contenedor scrollable para la lista de productos
        lista_productos = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=10
        )

        def filtrar_productos(e):
            filtro = filtro_field.value.lower()
            productos_filtrados = [producto for producto in productos if
                                   filtro in str(producto[0]).lower() or filtro in producto[1].lower()]
            actualizar_lista_productos(productos_filtrados)

        def actualizar_lista_productos(productos_filtrados):
            lista_productos.controls.clear()
            for producto in productos_filtrados:
                lista_productos.controls.append(self._crear_boton_producto(producto))
            self.page.update()

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre",
                                    on_change=filtrar_productos,
                                    width=500,
                                    border_color=ft.colors.OUTLINE)

        # Inicialmente, mostrar todos los productos
        actualizar_lista_productos(productos)

        # Agregar el contenedor scrollable a la página
        self.page.add(
            filtro_field,
            ft.Container(
                content=lista_productos,
                expand=True,
                height=400,  # Ajusta esta altura según tus necesidades
                width=500,  # Ajusta este ancho aquí dependiendo de tus necesidades
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
        """Crea un botón con la información del producto."""
        return ft.ElevatedButton(
            content=ft.Column(
                [
                    ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                            ft.Text(f"{producto[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ft.Row([ft.Text(f"Stock: ", color=BLUE_COLOR),
                            ft.Text(f"{producto[4]}", weight=ft.FontWeight.BOLD, color="white")]),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5,
            ),
            on_click=lambda _: self.consultar_producto(producto[0]),
            data=producto[0],
            width=500,  # Ajusta este ancho según tus necesidades
        )

    def consultar_producto(self, producto_id: int) -> None:
        """
        Consulta los detalles de un producto específico.

        Args:
            producto_id (int): ID del producto a consultar.
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
        """Obtiene los detalles de un producto específico desde la base de datos."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Productos WHERE id=?", (producto_id,))
            return cursor.fetchone()

    def _mostrar_formulario_producto(self, producto: Tuple = None) -> None:
        """
        Muestra el formulario para agregar o modificar un producto.

        Args:
            producto (Tuple, optional): Datos del producto a modificar. Si es None, se trata de un nuevo producto.
        """
        nombre_field = ft.TextField(label="Nombre", value=producto[1] if producto else "")
        descripcion_field = ft.TextField(label="Descripción", value=producto[2] if producto else "")
        precio_field = ft.TextField(label="Precio", value=str(producto[3]) if producto else "")
        stock_field = ft.TextField(label="Stock", value=str(producto[4]) if producto else "")
        # La siguiente linea lo que hace es desabilitar el campo para no ser modificado
        #stock_field = ft.TextField(label="Stock", disabled=True, value=str(producto[4]) if producto else "")

        def guardar_producto(_):
            try:
                self._validar_campos(nombre_field.value, descripcion_field.value, precio_field.value, stock_field.value)
                nuevo_producto = Producto(
                    nombre=nombre_field.value,
                    descripcion=descripcion_field.value,
                    precio=float(precio_field.value),
                    stock=int(stock_field.value),
                    id=producto[0] if producto else None
                )
                if producto:
                    nuevo_producto.update()
                else:
                    nuevo_producto.save()
                self.main_menu_callback()
            except ValueError as e:
                self.page.add(ft.Text(f"Error: {str(e)}", color=RED_COLOR))
                self.page.update()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Modificar Producto" if producto else "Agregar Producto", size=HEADER_SIZE),
            nombre_field,
            descripcion_field,
            precio_field,
            stock_field,
            ft.ElevatedButton("Guardar", on_click=guardar_producto),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _validar_campos(self, nombre: str, descripcion: str, precio: str, stock: str) -> None:
        """Valida los campos del formulario de producto."""
        if not nombre or not descripcion or not precio or not stock:
            raise ValueError("Todos los campos son obligatorios")
        try:
            float(precio)
        except ValueError:
            raise ValueError("El precio debe ser un número válido")
        try:
            int(stock)
        except ValueError:
            raise ValueError("El stock debe ser un número entero válido")

    def modificar(self, producto: Tuple) -> None:
        """
        Muestra la interfaz para modificar un producto existente.

        Args:
            producto (Tuple): Tupla que contiene los detalles del producto.
        """
        self._mostrar_formulario_producto(producto)

    def mostrar_mensaje(self, mensaje: str, color: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def eliminar(self, producto_id: int) -> None:
        """
        Elimina un producto de la base de datos.

        Args:
            producto_id (int): ID del producto a eliminar.
        """
        if self._producto_tiene_ventas(producto_id):
            self.mostrar_mensaje("El producto seleccionado tiene ventas registradas y no se puede eliminar", RED_COLOR)
            time.sleep(2)  # Esperar 2 segundos antes de volver al menú principal
            self.main_menu_callback()
        else:
            producto = Producto(id=producto_id, nombre="", descripcion="", precio=0, stock=0)
            producto.delete()
            self.main_menu_callback()

    def _producto_tiene_ventas(self, producto_id: int) -> bool:
        """
        Verifica si un producto tiene ventas registradas.

        Args:
            producto_id (int): ID del producto a verificar.

        Returns:
            bool: True si el producto tiene ventas, False en caso contrario.
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Ventas WHERE producto_id=?", (producto_id,))
            return cursor.fetchone()[0] > 0

    def agregar(self) -> None:
        """Muestra la interfaz para agregar un nuevo producto."""
        self._mostrar_formulario_producto()

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
    """
    Función principal que inicializa la aplicación de gestión de productos.

    Args:
        page (ft.Page): La página principal de la aplicación.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
    """
    app = ProductoApp(page, main_menu_callback)
    app.main_menu()

