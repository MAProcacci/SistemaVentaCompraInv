# graficos.py
import os
import flet as ft
from typing import Callable
from graficos_ventas import graficos_ventas_app
from graficos_clientes import graficos_clientes_app
from graf_ventas_diarias import grafico_ventas_diarias_app
from graf_dev_clientes import graf_devoluciones_clientes_app
from graf_dev_productos import graf_devoluciones_productos_app
from graf_comp_provee import graf_comp_provee_app
from graf_comp_producto import graf_comp_producto_app
from nav_graficos_pdf import nav_graficos_pdf_app

# Constantes
TITULO_GRAFICOS = "Gráficos"
COLOR_SNACKBAR = "white"

class GraficosApp:
    """
    Clase para la aplicación de gráficos.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.graficos_dir_pdf = os.path.join(os.getcwd(), 'Graficos_PDF')
        self.main_menu_callback = main_menu_callback

    def main_menu(self):
        """
        Muestra el menú principal de la aplicación.
        :return: None
        """
        def open_ventas_acumuladas(_):
            """
            Abre la interfaz de gráficos de ventas acumuladas por producto (Top 25)
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graficos_ventas_app(self.page, lambda: self.main_menu())

        def open_ventas_acumuladas_clientes(_):
            """
            Abre la interfaz de gráficos de ventas acumuladas por cliente (Top 25)
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graficos_clientes_app(self.page, lambda: self.main_menu())

        def open_ventas_diarias(_):
            """
            Abre la interfaz de gráficos de ventas diarias
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            grafico_ventas_diarias_app(self.page, lambda: self.main_menu())

        def open_devoluciones_clientes(_):
            """
            Abre la interfaz de gráficos de devoluciones por cliente
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graf_devoluciones_clientes_app(self.page, lambda: self.main_menu())

        def open_devoluciones_productos(_):
            """
            Abre la interfaz de gráficos de devoluciones por producto
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graf_devoluciones_productos_app(self.page, lambda: self.main_menu())

        def open_compras_proveedores(_):
            """
            Abre la interfaz de gráficos de compras por proveedor
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graf_comp_provee_app(self.page, lambda: self.main_menu())

        def open_compras_productos(_):
            """
            Abre la interfaz de gráficos de compras por producto
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            graf_comp_producto_app(self.page, lambda: self.main_menu())

        def open_nav_graficos_pdf(_):
            """
            Abre la interfaz de navegación de gráficos en PDF
            """
            self.page.controls.clear()  # Limpiar los controles actuales
            nav_graficos_pdf_app(self.page, lambda: self.main_menu())

        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_GRAFICOS, size=24),
            ft.ElevatedButton("Ventas Acumuladas por Producto (Top 25)", on_click=open_ventas_acumuladas),
            ft.ElevatedButton("Ventas Acumuladas por Cliente (Top 25)", on_click=open_ventas_acumuladas_clientes),
            ft.ElevatedButton("Ventas Diarias", on_click=open_ventas_diarias),
            ft.ElevatedButton("Devoluciones por Cliente (Top 25)", on_click=open_devoluciones_clientes),
            ft.ElevatedButton("Devoluciones por Producto (Top 25)", on_click=open_devoluciones_productos),
            ft.ElevatedButton("Compras por Proveedores (Top 25)", on_click=open_compras_proveedores),
            ft.ElevatedButton("Compras por Producto (Top 25)", on_click=open_compras_productos),
            ft.ElevatedButton("Navegar en Graficos PDF", on_click=lambda _: self.nav_graficos_pdf()),  # Agregar este botón al menu de Graficos
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def nav_graficos_pdf(self):
        """
        Abre la interfaz de navegación de gráficos en PDF.
        :return: None
        """
        #from nav_reportes_pdf import nav_reportes_pdf_app
        nav_graficos_pdf_app(self.page, self.graficos_dir_pdf, self.main_menu_callback)

def graficos_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Crea una instancia de la aplicación de gráficos y la ejecuta.
    :param page: La página de la aplicación.
    :param main_menu_callback: La función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = GraficosApp(page, main_menu_callback)
    app.main_menu()

