# graf_comp_provee.py
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

# Constantes
TITULO_COMPRAS_ACUMULADAS = "Top 25 Proveedores con Más Compras"
FORMATO_FECHA = '%Y-%m-%d'
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 600
COLOR_SNACKBAR = "white"

class GraficosComprasProveedores:
    """
    Clase para generar gráficos de compras acumuladas por proveedor.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.main_menu_callback = main_menu_callback

    def generar_grafico_compras_acumuladas(self, desde: str, hasta: str) -> str:
        """
        Genera un gráfico de barras de las compras acumuladas por proveedor.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :return: La ruta del archivo PDF generado.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.nombre, SUM(c.cantidad * c.precio_costo) AS total_compras
                FROM Compras c
                JOIN Proveedores p ON c.proveedor_id = p.id
                WHERE c.fecha BETWEEN ? AND ?
                GROUP BY p.nombre
                ORDER BY total_compras DESC
                LIMIT 25
            """
            cursor.execute(query, (desde, hasta))
            compras = cursor.fetchall()

        proveedores = [compra[0] for compra in compras]
        totales = [compra[1] for compra in compras]

        plt.switch_backend('Agg')
        plt.figure(figsize=(12, 6))
        plt.bar(proveedores, totales, color='green')
        plt.xlabel('Proveedores')
        plt.ylabel('Compras Acumuladas ($)')
        plt.title(f'Top 25 Proveedores con Más Compras ({desde} - {hasta})')
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
        Genera un archivo PDF con el gráfico de compras acumuladas por proveedor.
        :param image_base64: La imagen en formato base64.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :param orientation: Orientación del PDF (portrait o landscape).
        :return: La ruta del archivo PDF generado.
        """
        pdf_dir = os.path.join(os.getcwd(), 'Graficos_PDF')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'top_25_comp_provee_{desde}_{hasta}.pdf')

        if orientation == 'landscape':
            pagesize = landscape(letter)
        else:
            pagesize = letter

        doc = SimpleDocTemplate(pdf_path, pagesize=pagesize)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph(TITULO_COMPRAS_ACUMULADAS, styles['Title']))

        # Fecha de inicio y final
        elements.append(Paragraph(f"Fecha Inicio: {desde}", styles['Normal']))
        elements.append(Paragraph(f"Fecha Final: {hasta}", styles['Normal']))

        # Imagen del gráfico
        image_data = base64.b64decode(image_base64)
        elements.append(Image(io.BytesIO(image_data), width=700, height=400))

        doc.build(elements)

        return pdf_path

    def mostrar_grafico(self, desde: str, hasta: str):
        """
        Muestra el gráfico de compras acumuladas por proveedor en una ventana emergente.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        """
        image_base64 = self.generar_grafico_compras_acumuladas(desde, hasta)

        def close_dlg(_):
            """
            Cierra la ventana emergente.
            """
            dlg.open = False
            self.page.update()

        def generar_pdf_grafico(_):
            """
            Genera un archivo PDF con el gráfico de compras acumuladas por proveedor.
            """
            pdf_path = self.generar_pdf(image_base64, desde, hasta, orientation='landscape')
            self.mostrar_mensaje(f"PDF generado en: {pdf_path}")

        dlg = ft.AlertDialog(
            title=ft.Text(TITULO_COMPRAS_ACUMULADAS),
            content=ft.Column([
                ft.Row([
                    ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="green"),
                    ft.Text(desde),
                    ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="green"),
                    ft.Text(hasta)
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Image(src_base64=image_base64, width=ANCHO_GRAFICO, height=ALTO_GRAFICO, fit=ft.ImageFit.CONTAIN)
            ], scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cerrar", on_click=close_dlg),
                ft.TextButton("Generar PDF", on_click=generar_pdf_grafico)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def abrir_calendario(self, campo_fecha: ft.TextField):
        """
        Abre el calendario y actualiza el campo de fecha.
        :param campo_fecha: El campo de fecha a actualizar.
        :return: None
        """
        date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )

        def on_change(_):
            """
            Actualiza el campo de fecha con la fecha seleccionada.
            """
            if date_picker.value:
                campo_fecha.value = date_picker.value.strftime(FORMATO_FECHA)
                self.page.update()

        date_picker.on_change = on_change
        self.page.overlay.append(date_picker)
        self.page.update()
        date_picker.open = True
        self.page.update()

    def open_compras_acumuladas(self):
        """
        Abre la ventana de compras acumuladas.
        :return: None
        """
        desde_field = ft.TextField(label="Desde", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))
        hasta_field = ft.TextField(label="Hasta", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))

        def generar_grafico(_):
            """
            Genera el gráfico de compras acumuladas por proveedor.
            :return: None
            """
            desde = desde_field.value
            hasta = hasta_field.value

            try:
                desde_date = datetime.strptime(desde, FORMATO_FECHA)
                hasta_date = datetime.strptime(hasta, FORMATO_FECHA)
            except ValueError:
                self.mostrar_error("Formato de fecha incorrecto. Use YYYY-MM-DD.")
                return

            if hasta_date < desde_date:
                self.mostrar_error("La fecha 'Hasta' no puede ser menor que la fecha 'Desde'.")
                return

            self.mostrar_grafico(desde, hasta)

        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_COMPRAS_ACUMULADAS, size=24),
            ft.Column([
                self.crear_fila_fecha(desde_field, "Desde"),
                self.crear_fila_fecha(hasta_field, "Hasta")
            ]),
            ft.ElevatedButton("Generar Gráfico", on_click=generar_grafico),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def main_menu(self):
        """
        Muestra el menú principal de gráficos.
        :return: None
        """
        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_COMPRAS_ACUMULADAS, size=24),
            ft.ElevatedButton("Top 25 Proveedores con Más Compras", on_click=lambda _: self.open_compras_acumuladas()),
            ft.ElevatedButton("Volver al Menú de Gráficos", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def crear_fila_fecha(self, campo_fecha: ft.TextField, etiqueta: str) -> ft.Row:
        """
        Crea una fila con un campo de fecha y un botón para abrir el calendario.
        :param campo_fecha: El campo de fecha a mostrar.
        :param etiqueta: La etiqueta para el campo de fecha.
        :return: La fila con el campo de fecha y el botón para abrir el calendario.
        """
        return ft.Row([
            campo_fecha,
            ft.ElevatedButton(
                "Seleccionar Fecha",
                on_click=lambda _: self.abrir_calendario(campo_fecha),
                icon=ft.icons.CALENDAR_MONTH
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def mostrar_error(self, mensaje: str):
        """
        Muestra un mensaje de error en la interfaz.
        :param mensaje: El mensaje de error a mostrar.
        :return: None
        """
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar.open = True
        self.page.update()

    def mostrar_mensaje(self, mensaje: str):
        """
        Muestra un mensaje en la interfaz.
        :param mensaje: El mensaje a mostrar.
        :return: None
        """
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar.open = True
        self.page.update()

def graf_comp_provee_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Crea una instancia de la aplicación de gráficos de compras por proveedor y la ejecuta.
    :param page: La página principal de la aplicación.
    :param main_menu_callback: La función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = GraficosComprasProveedores(page, main_menu_callback)
    app.open_compras_acumuladas()

