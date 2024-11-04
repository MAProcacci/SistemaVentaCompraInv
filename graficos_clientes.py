# graficos_clientes.py
import flet as ft
from datetime import datetime
from database import create_connection
import matplotlib.pyplot as plt
import io
import base64
from typing import Callable
from libreria import BaseApp

# Constantes
TITULO_VENTAS_ACUMULADAS = "Top 25 Clientes con Más Ventas"
FORMATO_FECHA = '%Y-%m-%d'
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 600
COLOR_SNACKBAR = "white"

class GraficosClientes(BaseApp):
    """
    Clase para generar gráficos de ventas acumuladas de los clientes.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        super().__init__(page, main_menu_callback)

    def generar_grafico_ventas_acumuladas(self, desde: str, hasta: str) -> str:
        """
        Genera un gráfico de ventas acumuladas de los clientes.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :return: La imagen del gráfico en formato base64.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT c.nombre, SUM(v.cantidad * p.precio) AS total_ventas
                FROM Ventas v
                JOIN Productos p ON v.producto_id = p.id
                JOIN Clientes c ON v.cliente_id = c.id
                WHERE v.fecha BETWEEN ? AND ?
                GROUP BY c.nombre
                ORDER BY total_ventas DESC
                LIMIT 25
            """
            cursor.execute(query, (desde, hasta))
            ventas = cursor.fetchall()

        clientes = [venta[0] for venta in ventas]
        totales = [venta[1] for venta in ventas]

        plt.switch_backend('Agg')
        plt.figure(figsize=(12, 6))
        plt.bar(clientes, totales, color='blue')
        plt.xlabel('Clientes')
        plt.ylabel('Ventas Acumuladas ($)')
        plt.title(f'Top 25 Clientes con Más Ventas ({desde} - {hasta})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return image_base64

    def mostrar_grafico(self, desde: str, hasta: str):
        """
        Muestra el gráfico de ventas acumuladas de los clientes en la interfaz de usuario.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        """
        image_base64 = self.generar_grafico_ventas_acumuladas(desde, hasta)

        def close_dlg(_):
            """
            Cierra el diálogo de confirmación.
            :return: None
            """
            dlg.open = False
            self.page.update()

        def generar_pdf_grafico(_):
            """
            Genera un archivo PDF con el gráfico de ventas acumuladas de los clientes.
            :return: None
            """
            pdf_path = self.generar_pdf(image_base64, desde, hasta, TITULO_VENTAS_ACUMULADAS, orientation='landscape')
            self.mostrar_mensaje(f"PDF generado en: {pdf_path}", "blue")

        dlg = ft.AlertDialog(
            title=ft.Text(TITULO_VENTAS_ACUMULADAS),
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

    def open_ventas_acumuladas(self):
        """
        Abre la ventana de ventas acumuladas.
        :return: None
        """
        desde_field = ft.TextField(label="Desde", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))
        hasta_field = ft.TextField(label="Hasta", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))

        def generar_grafico(_):
            """
            Genera el gráfico de ventas acumuladas de los clientes.
            :return: None
            """
            desde = desde_field.value
            hasta = hasta_field.value

            if not self._validar_fechas(desde, hasta):
                return

            self.mostrar_grafico(desde, hasta)

        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_VENTAS_ACUMULADAS, size=24),
            ft.Column([
                self.crear_fila_fecha(desde_field, "Desde"),
                self.crear_fila_fecha(hasta_field, "Hasta")
            ]),
            ft.ElevatedButton("Generar Gráfico", on_click=generar_grafico),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

def graficos_clientes_app(page: ft.Page, main_menu_callback: Callable[[], None]):
    """
    Crea una instancia de la aplicación de gráficos de clientes y la ejecuta.
    :param page: La página de la aplicación.
    :param main_menu_callback: La función de devolución de llamada para volver al menú principal.
    :return: None
    """
    app = GraficosClientes(page, main_menu_callback)
    app.open_ventas_acumuladas()

