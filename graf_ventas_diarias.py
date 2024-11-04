# graf_ventas_diarias.py
import flet as ft
from datetime import datetime
from database import create_connection
import matplotlib.pyplot as plt
import io
import base64
from typing import Callable
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from libreria import BaseApp

# Constantes
TITULO_VENTAS_DIARIAS = "Ventas Diarias"
FORMATO_FECHA = '%Y-%m-%d'
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 600
COLOR_SNACKBAR = "white"

class GraficoVentasDiarias(BaseApp):
    """
    Clase para generar un gráfico de ventas diarias.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def generar_grafico_ventas_diarias(self, desde: str, hasta: str) -> str:
        """
        Genera un gráfico de ventas diarias.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :return: La imagen del gráfico en formato base64.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT v.fecha, SUM(v.cantidad * p.precio) AS total_ventas
                FROM Ventas v
                JOIN Productos p ON v.producto_id = p.id
                WHERE v.fecha BETWEEN ? AND ?
                GROUP BY v.fecha
            """
            cursor.execute(query, (desde, hasta))
            ventas = cursor.fetchall()

        fechas = [venta[0] for venta in ventas]
        totales = [venta[1] for venta in ventas]

        plt.switch_backend('Agg')
        plt.figure(figsize=(10, 6))
        plt.plot(fechas, totales, marker='o')
        plt.xlabel('Fecha')
        plt.ylabel('Ventas Totales ($)')
        plt.title(f'Ventas Diarias ({desde} - {hasta})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return image_base64

    def generar_pdf(self, image_base64: str, desde: str, hasta: str, orientation: str = 'portrait'):
        """
        Genera un archivo PDF con el gráfico de ventas diarias.
        :param image_base64: La imagen del gráfico en formato base64.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :param orientation: Orientación del PDF ('portrait' o 'landscape').
        :return: La ruta del archivo PDF generado.
        """
        pdf_dir = os.path.join(os.getcwd(), 'Graficos_PDF')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'ventas_diarias_{desde}_{hasta}.pdf')

        if orientation == 'landscape':
            pagesize = landscape(letter)
        else:
            pagesize = letter

        doc = SimpleDocTemplate(pdf_path, pagesize=pagesize)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph(TITULO_VENTAS_DIARIAS, styles['Title']))

        # Fecha de inicio y final
        elements.append(Paragraph(f"Fecha Inicio: {desde}", styles['Normal']))
        elements.append(Paragraph(f"Fecha Final: {hasta}", styles['Normal']))

        # Imagen del gráfico
        image_data = base64.b64decode(image_base64)
        elements.append(Image(io.BytesIO(image_data), width=500, height=300))

        doc.build(elements)

        return pdf_path

    def mostrar_grafico(self, desde: str, hasta: str):
        """
        Muestra el gráfico de ventas diarias en una ventana de diálogo.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        """
        image_base64 = self.generar_grafico_ventas_diarias(desde, hasta)

        def close_dlg(_):
            """
            Cierra la ventana de diálogo.
            :return: None
            """
            dlg.open = False
            self.page.update()

        def generar_pdf_grafico(_):
            """
            Genera un archivo PDF con el gráfico de ventas diarias.
            :return: None
            """
            pdf_path = self.generar_pdf(image_base64, desde, hasta, orientation='landscape')
            self.mostrar_mensaje(f"PDF generado en: {pdf_path}", "blue")

        dlg = ft.AlertDialog(
            title=ft.Text(TITULO_VENTAS_DIARIAS),
            content=ft.Column([
                ft.Row([
                    ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Text(desde),
                    ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Text(hasta)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Image(src_base64=image_base64, width=ANCHO_GRAFICO, height=ALTO_GRAFICO, fit=ft.ImageFit.CONTAIN)
            ], scroll=ft.ScrollMode.AUTO),  # Habilitar scroll en la columna
            actions=[
                ft.TextButton("Cerrar", on_click=close_dlg),
                ft.TextButton("Generar PDF", on_click=generar_pdf_grafico)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def open_ventas_diarias(self):
        """
        Abre la ventana de ventas diarias.
        :return: None
        """
        desde_field = ft.TextField(label="Desde", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))
        hasta_field = ft.TextField(label="Hasta", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))

        def generar_grafico(_):
            """
            Genera el gráfico de ventas diarias y muestra el resultado.
            :return: None
            """
            desde = desde_field.value
            hasta = hasta_field.value

            if not self._validar_fechas(desde, hasta):
                return

            self.mostrar_grafico(desde, hasta)

        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_VENTAS_DIARIAS, size=24),
            ft.Column([
                self.crear_fila_fecha(desde_field, "Desde"),
                self.crear_fila_fecha(hasta_field, "Hasta")
            ]),
            ft.ElevatedButton("Generar Gráfico", on_click=generar_grafico),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def grafico_ventas_diarias_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Crea una instancia de la aplicación de gráfico de ventas diarias y la ejecuta.
    :param page: Instancia de la clase Page de flet.
    :param main_menu_callback: Función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = GraficoVentasDiarias(page, main_menu_callback)
    app.open_ventas_diarias()

