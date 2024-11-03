# nav_facturas_pdf.py
import flet as ft
import os
import subprocess
import platform
from libreria import BaseApp

class NavFacturasPDF(BaseApp):
    """
    Clase para la navegación de facturas en formato PDF.
    """
    def __init__(self, page: ft.Page, facturas_dir: str, main_menu_callback: callable):
        super().__init__(page, main_menu_callback)
        self.facturas_dir = facturas_dir
        self.facturas = []
        self.filtered_facturas = []
        self.selected_factura = None
        self.filtro_field = ft.TextField(label="Filtrar por Número de Factura", on_change=self.filtrar_facturas, width=500, border_color=ft.colors.OUTLINE)

    def cargar_facturas(self):
        """
        Carga las facturas desde el directorio especificado.
        :return: None
        """
        self.facturas = [f for f in os.listdir(self.facturas_dir) if f.endswith('.pdf')]
        self.filtered_facturas = self.facturas
        self.mostrar_facturas()

    def mostrar_facturas(self, e=None):
        """
        Muestra las facturas en la interfaz.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text("Facturas PDF", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))
        self.page.add(self.filtro_field)

        list_view = ft.ListView(expand=True, spacing=10)
        for factura in self.filtered_facturas:
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(factura),
                    on_click=lambda e, f=factura: self.seleccionar_factura(f)
                )
            )
        self.page.add(list_view)
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback()))
        self.page.update()

    def seleccionar_factura(self, factura: str):
        """
        Selecciona una factura y muestra las opciones disponibles.
        :param factura: El nombre de la factura seleccionada.
        :return: None
        """
        self.selected_factura = factura
        self.mostrar_opciones()

    def mostrar_opciones(self, e=None):
        """
        Muestra las opciones disponibles para la factura seleccionada.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text(f"Opciones para: {self.selected_factura}", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        self.page.add(ft.ElevatedButton("Ver", on_click=self.ver_factura))
        self.page.add(ft.ElevatedButton("Imprimir", on_click=self.imprimir_factura))
        self.page.add(ft.ElevatedButton("Volver", on_click=self.mostrar_facturas))
        self.page.update()

    def ver_factura(self, e):
        """
        Verifica si el sistema operativo es Windows y abre la factura en SumatraPDF.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_factura:
            ruta_factura = os.path.join(self.facturas_dir, self.selected_factura)
            try:
                if os.name == 'nt':  # Windows
                    sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                    subprocess.run([sumatra_path, ruta_factura], check=True)
                else:
                    raise OSError("Sistema operativo no soportado para abrir archivos PDF")
            except Exception as e:
                self.mostrar_mensaje(f"Error al abrir la factura: {str(e)}", "red")

    def imprimir_factura(self, e):
        """
        Imprime la factura seleccionada.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_factura:
            ruta_factura = os.path.join(self.facturas_dir, self.selected_factura)
            try:
                if os.name == 'nt':  # Windows
                    sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                    subprocess.run([sumatra_path, '-print-to-default', ruta_factura], check=True)
                elif os.name == 'posix':  # macOS o Linux
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['lpr', ruta_factura], check=True)
                    else:  # Linux
                        subprocess.run(['lp', ruta_factura], check=True)
                else:
                    raise OSError("Sistema operativo no soportado para imprimir")
            except Exception as e:
                self.mostrar_mensaje(f"Error al imprimir: {str(e)}", "red")

    def filtrar_facturas(self, e):
        """
        Filtra las facturas según el valor ingresado en el campo de filtro.
        :param e: Evento de cambio de estado.
        :return: None
        """
        filtro = self.filtro_field.value.lower()
        self.filtered_facturas = [f for f in self.facturas if filtro in f.lower()]
        self.mostrar_facturas()

def nav_facturas_pdf_app(page: ft.Page, facturas_dir: str, main_menu_callback: callable):
    """
    Crea una instancia de la clase NavFacturasPDF y carga las facturas.
    :param page: Página de la interfaz.
    :param facturas_dir: Directorio donde se encuentran las facturas.
    :param main_menu_callback: Función de retorno al menú principal.
    :return: None
    """
    app = NavFacturasPDF(page, facturas_dir, main_menu_callback)
    app.cargar_facturas()

