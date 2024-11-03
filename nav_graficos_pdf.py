# nav_graficos_pdf.py
import flet as ft
import os
import subprocess
import platform
from libreria import BaseApp

class NavGraficosPDF(BaseApp):
    """
    Clase para mostrar los gráficos PDF en una lista y permitir la selección de uno para abrirlo.
    """
    def __init__(self, page: ft.Page, graficos_dir: str, main_menu_callback: callable):
        super().__init__(page, main_menu_callback)
        self.graficos_dir = graficos_dir
        self.graficos = []
        self.selected_grafico = None

    def cargar_graficos(self):
        """
        Carga los gráficos PDF desde el directorio especificado.
        :return: None
        """
        self.graficos = [f for f in os.listdir(self.graficos_dir) if f.endswith('.pdf')]
        self.mostrar_graficos()

    def mostrar_graficos(self, e=None):
        """
        Muestra los gráficos PDF en una lista y permite seleccionar uno para abrirlo.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text("Gráficos PDF", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        list_view = ft.ListView(expand=True, spacing=10)
        for grafico in self.graficos:
            list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(grafico),
                    on_click=lambda e, g=grafico: self.seleccionar_grafico(g)
                )
            )
        self.page.add(list_view)
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback()))
        self.page.update()

    def seleccionar_grafico(self, grafico: str):
        """
        Selecciona un gráfico PDF para abrirlo.
        :param grafico: Nombre del gráfico PDF a abrir.
        :return: None
        """
        self.selected_grafico = grafico
        self.mostrar_opciones()

    def mostrar_opciones(self, e=None):
        """
        Muestra las opciones disponibles para el gráfico seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(ft.Text(f"Opciones para: {self.selected_grafico}", size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        self.page.add(ft.ElevatedButton("Eliminar", on_click=self.confirmar_eliminar))
        self.page.add(ft.ElevatedButton("Ver", on_click=self.ver_grafico))
        self.page.add(ft.ElevatedButton("Imprimir", on_click=self.imprimir_grafico))
        self.page.add(ft.ElevatedButton("Volver", on_click=self.mostrar_graficos))
        self.page.update()

    def confirmar_eliminar(self, e):
        """
        Muestra un cuadro de diálogo de confirmación para eliminar un gráfico PDF.
        :param e: Evento de cambio de estado.
        :return: None
        """
        def eliminar(_):
            """
            Eliminar el gráfico seleccionado.
            :return: None
            """
            self.eliminar_grafico()
            self.page.dialog.open = False
            self.page.update()

        def cancelar(_):
            """
            Cerrar el cuadro de diálogo de confirmación.
            :return: None
            """
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text("¿Desea borrar este gráfico?"),
            actions=[
                ft.TextButton("Sí", on_click=eliminar),
                ft.TextButton("No", on_click=cancelar)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def eliminar_grafico(self):
        """
        Elimina el gráfico seleccionado.
        :return: None
        """
        if self.selected_grafico:
            ruta_grafico = os.path.join(self.graficos_dir, self.selected_grafico)
            os.remove(ruta_grafico)
            self.graficos.remove(self.selected_grafico)
            self.mostrar_mensaje(f"Gráfico {self.selected_grafico} eliminado.")
            self.selected_grafico = None
            self.mostrar_graficos()

    def ver_grafico(self, e):
        """
        Abre el gráfico PDF seleccionado en el visor de PDF.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_grafico:
            ruta_grafico = os.path.join(self.graficos_dir, self.selected_grafico)
            try:
                if os.name == 'nt':  # Windows
                    sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                    subprocess.run([sumatra_path, ruta_grafico], check=True)
                else:
                    raise OSError("Sistema operativo no soportado para abrir archivos PDF")
            except Exception as e:
                self.mostrar_mensaje(f"Error al abrir el gráfico: {str(e)}", "red")

    def imprimir_grafico(self, e):
        """
        Imprime el gráfico PDF seleccionado.
        :param e: Evento de cambio de estado.
        :return: None
        """
        if self.selected_grafico:
            ruta_reporte = os.path.join(self.graficos_dir, self.selected_grafico)
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

def nav_graficos_pdf_app(page: ft.Page, graficos_dir: str, main_menu_callback: callable):
    """
    Crea una instancia de la aplicación de navegación de gráficos PDF y la ejecuta.
    :param page: Página de la interfaz gráfica.
    :param graficos_dir: Directorio donde se almacenan los gráficos PDF.
    :param main_menu_callback: Función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = NavGraficosPDF(page, graficos_dir, main_menu_callback)
    app.cargar_graficos()
