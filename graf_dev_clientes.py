# graf_dev_clientes.py
import flet as ft
from typing import Callable
from libreria import BaseApp

# Constantes
TITULO_DEVOLUCIONES_CLIENTES = "Top 25 Clientes con Más Devoluciones"
FORMATO_FECHA = '%Y-%m-%d'
COLOR_SNACKBAR = "white"

class GraficoDevolucionesClientes(BaseApp):
    """
    Clase para generar y mostrar un gráfico de devoluciones de clientes.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def open_devoluciones_clientes(self):
        """
        Abre la ventana de devoluciones de clientes.
        :return: None
        """
        query = """
            SELECT c.nombre, SUM(d.cantidad * p.precio) AS total_devoluciones
            FROM Devoluciones d
            JOIN Clientes c ON d.cliente_id = c.id
            JOIN Productos p ON d.producto_id = p.id
            WHERE d.fecha BETWEEN ? AND ?
            GROUP BY c.id
            ORDER BY total_devoluciones DESC
            LIMIT 25
        """
        super().open_compras_o_devoluciones(TITULO_DEVOLUCIONES_CLIENTES, query, 'red')

def graf_devoluciones_clientes_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Abre la ventana de devoluciones de clientes.
    :param page: La página principal de la aplicación.
    :param main_menu_callback: La función de devolución al menú principal.
    :return: None
    """
    app = GraficoDevolucionesClientes(page, main_menu_callback)
    app.open_devoluciones_clientes()
