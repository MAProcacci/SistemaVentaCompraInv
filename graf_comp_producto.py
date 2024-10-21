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
TITULO_COMPRAS_ACUMULADAS = "Top 25 Productos con Más Compras"
FORMATO_FECHA = '%Y-%m-%d'
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 600
COLOR_SNACKBAR = "white"

class GraficosComprasProductos:
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.main_menu_callback = main_menu_callback

    def generar_grafico_compras_acumuladas(self, desde: str, hasta: str) -> str:
        with create_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT p.nombre, SUM(c.cantidad * c.precio_costo) AS total_compras
                FROM Compras c
                JOIN Productos p ON c.producto_id = p.id
                WHERE c.fecha BETWEEN ? AND ?
                GROUP BY p.nombre
                ORDER BY total_compras DESC
                LIMIT 25
            """
            cursor.execute(query, (desde, hasta))
            compras = cursor.fetchall()

        productos = [compra[0] for compra in compras]
        totales = [compra[1] for compra in compras]

        plt.switch_backend('Agg')
        plt.figure(figsize=(12, 6))
        plt.bar(productos, totales, color='blue')
        plt.xlabel('Productos')
        plt.ylabel('Compras Acumuladas ($)')
        plt.title(f'Top 25 Productos con Más Compras ({desde} - {hasta})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return image_base64

    def generar_pdf(self, image_base64: str, desde: str, hasta: str, orientation: str = 'portrait'):
        pdf_dir = os.path.join(os.getcwd(), 'Graficos_PDF')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, f'top_25_comp_prod_{desde}_{hasta}.pdf')

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
        image_base64 = self.generar_grafico_compras_acumuladas(desde, hasta)

        def close_dlg(_):
            dlg.open = False
            self.page.update()

        def generar_pdf_grafico(_):
            pdf_path = self.generar_pdf(image_base64, desde, hasta, orientation='landscape')
            self.mostrar_mensaje(f"PDF generado en: {pdf_path}")

        dlg = ft.AlertDialog(
            title=ft.Text(TITULO_COMPRAS_ACUMULADAS),
            content=ft.Column([
                ft.Row([
                    ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
                    ft.Text(desde),
                    ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
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
        date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )

        def on_change(_):
            if date_picker.value:
                campo_fecha.value = date_picker.value.strftime(FORMATO_FECHA)
                self.page.update()

        date_picker.on_change = on_change
        self.page.overlay.append(date_picker)
        self.page.update()
        date_picker.open = True
        self.page.update()

    def open_compras_acumuladas(self):
        desde_field = ft.TextField(label="Desde", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))
        hasta_field = ft.TextField(label="Hasta", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))

        def generar_grafico(_):
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
        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_COMPRAS_ACUMULADAS, size=24),
            ft.ElevatedButton("Top 25 Productos con Más Compras", on_click=lambda _: self.open_compras_acumuladas()),
            ft.ElevatedButton("Volver al Menú de Gráficos", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def crear_fila_fecha(self, campo_fecha: ft.TextField, etiqueta: str) -> ft.Row:
        return ft.Row([
            campo_fecha,
            ft.ElevatedButton(
                "Seleccionar Fecha",
                on_click=lambda _: self.abrir_calendario(campo_fecha),
                icon=ft.icons.CALENDAR_MONTH
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def mostrar_error(self, mensaje: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar.open = True
        self.page.update()

    def mostrar_mensaje(self, mensaje: str):
        self.page.snack_bar = ft.SnackBar(ft.Text(mensaje, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar.open = True
        self.page.update()

def graf_comp_producto_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    app = GraficosComprasProductos(page, main_menu_callback)
    app.open_compras_acumuladas()