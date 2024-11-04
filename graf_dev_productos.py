# graf_dev_productos.py
import flet as ft
from typing import Callable
from libreria import BaseApp

# Constantes
TITULO_DEVOLUCIONES_PRODUCTOS = "Top 25 Productos con Más Devoluciones"
FORMATO_FECHA = '%Y-%m-%d'
COLOR_SNACKBAR = "white"

class GraficoDevolucionesProductos(BaseApp):
    """
    Clase para generar el gráfico de devoluciones de productos.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def open_devoluciones_productos(self):
        """
        Abre el diálogo de devoluciones de productos.
        :return: None
        """
        query = """
            SELECT p.nombre, SUM(d.cantidad * p.precio) AS total_devoluciones
            FROM Devoluciones d
            JOIN Productos p ON d.producto_id = p.id
            WHERE d.fecha BETWEEN ? AND ?
            GROUP BY p.id
            ORDER BY total_devoluciones DESC
            LIMIT 25
        """
        super().open_compras_o_devoluciones(TITULO_DEVOLUCIONES_PRODUCTOS, query, 'orange')

def graf_devoluciones_productos_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Función principal del módulo.
    :param page: Página de la aplicación.
    :param main_menu_callback: Función de retorno al menú principal.
    :return: None
    """
    app = GraficoDevolucionesProductos(page, main_menu_callback)
    app.open_devoluciones_productos()
