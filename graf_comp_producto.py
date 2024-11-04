# graf_comp_producto.py
import flet as ft
from typing import Callable
from libreria import BaseApp

# Constantes
TITULO_COMPRAS_ACUMULADAS = "Top 25 Productos con Más Compras"
FORMATO_FECHA = '%Y-%m-%d'
COLOR_SNACKBAR = "white"

class GraficosComprasProductos(BaseApp):
    """
    Esta clase se encarga de generar los gráficos de compras acumuladas y compras por categoría.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def open_compras_acumuladas(self):
        """
        Abre la ventana de compras acumuladas.
        :return: None
        """
        query = """
            SELECT p.nombre, SUM(c.cantidad * c.precio_costo) AS total_compras
            FROM Compras c
            JOIN Productos p ON c.producto_id = p.id
            WHERE c.fecha BETWEEN ? AND ?
            GROUP BY p.nombre
            ORDER BY total_compras DESC
            LIMIT 25
        """
        super().open_compras_o_devoluciones(TITULO_COMPRAS_ACUMULADAS, query, 'blue')

def graf_comp_producto_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Crea una instancia de la aplicación de gráficos de compras por producto y la ejecuta.
    :param page: La página de la interfaz de usuario.
    :param main_menu_callback: La función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = GraficosComprasProductos(page, main_menu_callback)
    app.open_compras_acumuladas()
