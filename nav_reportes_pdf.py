# nav_reportes_pdf.py
import flet as ft
import os
import subprocess
import platform
from libreria import BaseApp

class NavReportesPDF(BaseApp):
    """
    Clase para la navegación de reportes PDF.
    """
    def __init__(self, page: ft.Page, reportes_dir: str, main_menu_callback: callable):
        super().__init__(page, main_menu_callback)
        self.reportes_dir = reportes_dir
        self.reportes = []
        self.selected_report = None

    def cargar_reportes(self):
        """
        Carga los reportes PDF disponibles en el directorio especificado.
        :return: None
        """
        self.reportes = [f for f in os.listdir(self.reportes_dir) if f.endswith('.pdf')]
        self.mostrar_reportes()

    def mostrar_reportes(self, e=None):
        """
        Muestra los reportes PDF disponibles en una lista.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text("Reportes PDF", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        list_view = ft.ListView(expand=True, spacing=10)
        for reporte in self.reportes:
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(reporte),
                    on_click=lambda e, r=reporte: self.seleccionar_reporte(r)
                )
            )
        self.page.add(list_view)
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback()))
        self.page.update()

    def seleccionar_reporte(self, reporte: str):
        """
        Selecciona un reporte PDF para mostrar sus opciones.
        :param reporte: Nombre del reporte PDF.
        :return: None
        """
        self.selected_report = reporte
        self.mostrar_opciones()

    def mostrar_opciones(self, e=None):
        """
        Muestra las opciones disponibles para el reporte seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text(f"Opciones para: {self.selected_report}", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        self.page.add(ft.ElevatedButton("Eliminar", on_click=self.confirmar_eliminar))
        self.page.add(ft.ElevatedButton("Ver", on_click=self.ver_reporte))
        self.page.add(ft.ElevatedButton("Imprimir", on_click=self.imprimir_reporte))
        self.page.add(ft.ElevatedButton("Volver", on_click=self.mostrar_reportes))
        self.page.update()

    def confirmar_eliminar(self, e):
        """
        Confirma la eliminación del reporte seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        def eliminar(_):
            """
            Confirma la eliminación del reporte seleccionado.
            :return: None
            """
            self.eliminar_reporte()
            self.page.dialog.open = False
            self.page.update()

        def cancelar(_):
            """
            Cancela la eliminación del reporte seleccionado.
            :return: None
            """
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Desea borrar este reporte?"),
            actions=[
                ft.TextButton("Sí", on_click=eliminar),
                ft.TextButton("No", on_click=cancelar)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def eliminar_reporte(self):
        """
        Elimina el reporte seleccionado.
        :return: None
        """
        if self.selected_report:
            ruta_reporte = os.path.join(self.reportes_dir, self.selected_report)
            os.remove(ruta_reporte)
            self.reportes.remove(self.selected_report)
            self.mostrar_mensaje(f"Reporte {self.selected_report} eliminado.")
            self.selected_report = None
            self.mostrar_reportes()

    def ver_reporte(self, e):
        """
        Ver el reporte seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_report:
            ruta_reporte = os.path.join(self.reportes_dir, self.selected_report)
            try:
                if os.name == 'nt':  # Windows
                    sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                    subprocess.run([sumatra_path, ruta_reporte], check=True)
                else:
                    raise OSError("Sistema operativo no soportado para abrir archivos PDF")
            except Exception as e:
                self.mostrar_mensaje(f"Error al abrir el reporte: {str(e)}", "red")

    def imprimir_reporte(self, e):
        """
        Imprimir el reporte seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_report:
            ruta_reporte = os.path.join(self.reportes_dir, self.selected_report)
            try:
                if os.name == 'nt':  # Windows
                    sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                    subprocess.run([sumatra_path, '-print-to-default', ruta_reporte], check=True)
                elif os.name == 'posix':  # macOS o Linux
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['lpr', ruta_reporte], check=True)
                    else:  # Linux
                        subprocess.run(['lp', ruta_reporte], check=True)
                else:
                    raise OSError("Sistema operativo no soportado para imprimir")
            except Exception as e:
                self.mostrar_mensaje(f"Error al imprimir: {str(e)}", "red")

def nav_reportes_pdf_app(page: ft.Page, reportes_dir: str, main_menu_callback: callable):
    """
    Crea una instancia de la aplicación de navegación de reportes PDF.
    :param page: Página de la aplicación.
    :param reportes_dir: Directorio donde se almacenan los reportes.
    :param main_menu_callback: Función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = NavReportesPDF(page, reportes_dir, main_menu_callback)
    app.cargar_reportes()
