# libreria.py
import flet as ft
from typing import Callable, List, Tuple, Optional, Any
from contextlib import contextmanager
from database import create_connection
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image

# Constantes
BLUE_COLOR = "blue"
RED_COLOR = "red"
HEADER_SIZE = 24
BUTTON_TEXT_SIZE = 16
COLOR_SNACKBAR = "white"
FORMATO_FECHA = '%Y-%m-%d'
ANCHO_GRAFICO = 800
ALTO_GRAFICO = 600

@contextmanager
def get_db_connection():
    """
    Administrador de contexto para manejar conexiones a la base de datos.

    Yields:
        Connection: Objeto de conexión a la base de datos.
    """
    conn = create_connection()
    try:
        yield conn
    finally:
        conn.close()

def _crear_menu_fila(text1: str, on_click1: Callable,
                     text2: str, on_click2: Callable) -> ft.Row:
    """Crea una fila de botones de 2 columnas para el menú en 'Flet'.
    Args:
        text1 (str): Texto del botón 1.
        on_click1 (Callable): Función que se llama cuando se hace click en el botón 1.
        text2 (str): Texto del botón 2.
        on_click2 (Callable): Función que se llama cuando se hace click en el botón 2.
        """
    return ft.Row([
        ft.ElevatedButton(text1, on_click=on_click1),
        ft.Divider(height=20, color="transparent"),
        ft.ElevatedButton(text2, on_click=on_click2),
    ], alignment=ft.MainAxisAlignment.CENTER)

@dataclass
class FormField:
    """
    Clase que representa un campo de formulario.

    Attributes:
        label (str): Etiqueta del campo.
        value (Optional[str]): Valor inicial del campo. Por defecto es None.
    """
    label: str
    value: Optional[str] = None

class BaseApp:
    """
    Clase base para las aplicaciones que utilizan la interfaz de usuario.

    Attributes:
        page (ft.Page): Página de la aplicación.
        main_menu_callback (Callable[[], None]): Función de devolución de llamada para volver al menú principal.
    """
    def __init__(self, page: ft.Page, main_menu_callback: Callable[[], None]):
        self.page = page
        self.main_menu_callback = main_menu_callback

    def _agregar_reporte(self, titulo: str, elementos: List[Any], desde: Optional[str] = None,
                         hasta: Optional[str] = None):
        """
        Agrega un reporte a la página.

        Args:
            titulo (str): Título del reporte.
            elementos (List[Any]): Lista de elementos a mostrar en el reporte.
            desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
            hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        """
        self.page.controls.clear()
        self.page.add(ft.Text(titulo, size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))

        if desde and hasta:
            self.page.add(ft.Row([
                ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(desde),
                ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(hasta)
            ], alignment=ft.MainAxisAlignment.CENTER))

        column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        list_view = ft.ListView(expand=True, spacing=10, controls=elementos)
        column.controls.append(list_view)
        self.page.add(ft.Container(content=column, expand=True))

        self.page.add(ft.ElevatedButton("Generar CSV", on_click=lambda _: self.generar_csv_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Generar PDF", on_click=lambda _: self.generar_pdf_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def mostrar_mensaje(self, mensaje: str, color: str):
        """
        Muestra un mensaje en la barra de notificaciones.

        Args:
            mensaje (str): Mensaje a mostrar.
            color (str): Color del texto del mensaje.
        """
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def _crear_boton_entidad(self, entidad: Tuple, entidad_name: str, on_click: Callable) -> ft.ElevatedButton:
        """
        Crea un botón con la información de la entidad.

        Args:
            entidad (Tuple): Datos de la entidad.
            entidad_name (str): Nombre de la entidad.
            on_click (Callable): Función de devolución de llamada al hacer clic en el botón.

        Returns:
            ft.ElevatedButton: Botón con la información de la entidad.
        """
        if entidad_name == "Producto":
            return ft.ElevatedButton(
                content=ft.Column(
                    [
                        ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                        ft.Row([ft.Text(f"Stock: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[4]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=on_click,
                data=entidad[0],
                width=500,  # Ajusta este ancho según tus necesidades
            )
        else:
            return ft.ElevatedButton(
                content=ft.Column(
                    [
                        ft.Row([ft.Text(f"Nombre: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[1]}", weight=ft.FontWeight.BOLD, color="white")]),
                        ft.Row([ft.Text(f"Teléfono: ", color=BLUE_COLOR),
                                ft.Text(f"{entidad[2]}", weight=ft.FontWeight.BOLD, color="white")]),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5,
                ),
                on_click=on_click,
                data=entidad[0],
                width=500,  # Ajusta este ancho según tus necesidades
            )

    def _mostrar_formulario_entidad(self, entidad: Tuple = None, entidad_name: str = "Entidad", campos: List[FormField] = [], guardar_callback: Callable = None) -> None:
        """
        Muestra el formulario para agregar o modificar una entidad.

        Args:
            entidad (Tuple, optional): Datos de la entidad a modificar. Si es None, se trata de una nueva entidad.
            entidad_name (str): Nombre de la entidad.
            campos (List[FormField]): Lista de campos del formulario.
            guardar_callback (Callable): Función de devolución de llamada para guardar la entidad.
        """
        fields = [ft.TextField(label=field.label, value=field.value if entidad else "") for field in campos]

        def guardar_entidad(_):
            try:
                if guardar_callback:
                    guardar_callback(fields, entidad)  # Pasar entidad como argumento
                self.main_menu_callback()
            except ValueError as e:
                self.mostrar_mensaje(f"Error: {str(e)}", RED_COLOR)
                self.page.update()
            except Exception as e:
                self.mostrar_mensaje(f"Error inesperado: {str(e)}", RED_COLOR)

        self.page.controls.clear()
        self.page.add(
            ft.Text(f"Modificar {entidad_name}" if entidad else f"Agregar {entidad_name}", size=HEADER_SIZE),
            *fields,
            ft.ElevatedButton("Guardar", on_click=guardar_entidad),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _validar_campos(self, campos: List[ft.TextField]) -> None:
        """
        Valida los campos del formulario.

        Args:
            campos (List[ft.TextField]): Lista de campos del formulario.

        Raises:
            ValueError: Si algún campo está vacío.
        """
        for field in campos:
            if not field.value:
                raise ValueError("Todos los campos son obligatorios")

    def abrir_calendario(self, e, campo_fecha: ft.TextField):
        """
        Abre un calendario para seleccionar una fecha.

        Args:
            e: Evento de Flet.
            campo_fecha (ft.TextField): Campo de texto donde se mostrará la fecha seleccionada.
        """
        date_picker = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )

        def on_change(e):
            if date_picker.value:
                campo_fecha.value = date_picker.value.strftime('%Y-%m-%d')
                self.page.update()

        date_picker.on_change = on_change
        self.page.overlay.append(date_picker)
        self.page.update()
        date_picker.open = True
        self.page.update()

    def _validar_fechas(self, desde: str, hasta: str) -> bool:
        """
        Valida que la fecha 'Hasta' no sea menor que la fecha 'Desde'.

        Args:
            desde (str): Fecha de inicio.
            hasta (str): Fecha de fin.

        Returns:
            bool: True si las fechas son válidas, False en caso contrario.
        """
        try:
            desde_date = datetime.strptime(desde, '%Y-%m-%d')
            hasta_date = datetime.strptime(hasta, '%Y-%m-%d')
            if hasta_date < desde_date:
                raise ValueError("La fecha 'Hasta' no puede ser menor que la fecha 'Desde'.")
            return True
        except ValueError as e:
            self.mostrar_mensaje(f"Error: {str(e)}", RED_COLOR)
            return False

    def generar_grafico_devoluciones(self, desde: str, hasta: str, titulo: str, query: str, color: str) -> str:
        """
        Genera un gráfico de devoluciones y lo guarda en un archivo PDF.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :param titulo: Título del gráfico.
        :param query: Consulta SQL para obtener los datos.
        :param color: Color del gráfico.
        :return: La imagen del gráfico en formato base64.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (desde, hasta))
            devoluciones = cursor.fetchall()

        nombres = [dev[0] for dev in devoluciones]
        totales = [dev[1] for dev in devoluciones]

        plt.switch_backend('Agg')
        plt.figure(figsize=(12, 6))
        plt.bar(nombres, totales, color=color)
        plt.xlabel('Nombres')
        plt.ylabel('Total Devoluciones ($)')
        plt.title(f'{titulo} ({desde} - {hasta})')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()

        return image_base64

    def generar_pdf(self, image_base64: str, desde: str, hasta: str, titulo: str, orientation: str = 'portrait'):
        """
        Genera un archivo PDF con el gráfico de devoluciones.
        :param image_base64: La imagen del gráfico en formato base64.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :param titulo: Título del gráfico.
        :param orientation: Orientación del PDF (portrait o landscape).
        :return: La ruta del archivo PDF generado.
        """
        pdf_dir = os.path.join(os.getcwd(), 'Graficos_PDF')
        os.makedirs(pdf_dir, exist_ok=True)
        if titulo == "Top 25 Productos con Más Compras":
            titulo_archivo = "top_25_comp_prod"
        elif titulo == "Top 25 Proveedores con Más Compras":
            titulo_archivo = "top_25_comp_provee"
        elif titulo == "Top 25 Productos con Más Devoluciones":
            titulo_archivo = "top_25_devoluciones_productos"
        elif titulo == "Top 25 Clientes con Más Devoluciones":
            titulo_archivo = "top_25_devoluciones_clientes"
        elif titulo == "Top 25 Productos con Más Ventas":
            titulo_archivo = "top_25_ventas_producto"
        elif titulo == "Top 25 Clientes con Más Ventas":
            titulo_archivo = "top_25_ventas_clientes"

        pdf_path = os.path.join(pdf_dir, f'{titulo_archivo.lower().replace(" ", "_")}_{desde}_{hasta}.pdf')

        if orientation == 'landscape':
            pagesize = landscape(letter)
        else:
            pagesize = letter

        doc = SimpleDocTemplate(pdf_path, pagesize=pagesize)
        styles = getSampleStyleSheet()
        elements = []

        # Título
        elements.append(Paragraph(titulo, styles['Title']))

        # Fecha de inicio y final
        elements.append(Paragraph(f"Fecha Inicio: {desde}", styles['Normal']))
        elements.append(Paragraph(f"Fecha Final: {hasta}", styles['Normal']))

        # Imagen del gráfico
        image_data = base64.b64decode(image_base64)
        elements.append(Image(io.BytesIO(image_data), width=700, height=400))

        doc.build(elements)

        return pdf_path

    def mostrar_grafico(self, desde: str, hasta: str, titulo: str, generar_grafico_callback: Callable, generar_pdf_callback: Callable):
        """
        Muestra el gráfico de devoluciones en una ventana emergente.
        :param desde: Fecha de inicio del rango de fechas.
        :param hasta: Fecha de fin del rango de fechas.
        :param titulo: Título del gráfico.
        :param generar_grafico_callback: Función de devolución de llamada para generar el gráfico.
        :param generar_pdf_callback: Función de devolución de llamada para generar el PDF.
        """
        image_base64 = generar_grafico_callback(desde, hasta)

        def close_dlg(_):
            """
            Cierra la ventana emergente.
            """
            dlg.open = False
            self.page.update()

        def generar_pdf_grafico(_):
            """
            Genera un archivo PDF con el gráfico de devoluciones.
            """
            pdf_path = generar_pdf_callback(image_base64, desde, hasta)
            self.mostrar_mensaje(f"PDF generado en: {pdf_path}", BLUE_COLOR)

        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
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

    def open_compras_o_devoluciones(self, titulo: str, query: str, color: str):
        """
        Abre la ventana de devoluciones.
        :param titulo: Título del gráfico.
        :param query: Consulta SQL para obtener los datos.
        :param color: Color del gráfico.
        :return: None
        """
        desde_field = ft.TextField(label="Desde", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))
        hasta_field = ft.TextField(label="Hasta", hint_text=FORMATO_FECHA,
                                   value=datetime.today().strftime(FORMATO_FECHA))

        def generar_grafico(_):
            """
            Genera el gráfico de devoluciones.
            :return: None
            """
            desde = desde_field.value
            hasta = hasta_field.value

            try:
                desde_date = datetime.strptime(desde, FORMATO_FECHA)
                hasta_date = datetime.strptime(hasta, FORMATO_FECHA)
            except ValueError:
                self.mostrar_mensaje("Formato de fecha incorrecto. Use YYYY-MM-DD.", RED_COLOR)
                return

            if hasta_date < desde_date:
                self.mostrar_mensaje("La fecha 'Hasta' no puede ser menor que la fecha 'Desde'.", RED_COLOR)
                return

            self.mostrar_grafico(desde, hasta, titulo,
                                 lambda desde, hasta: self.generar_grafico_devoluciones(desde, hasta, titulo, query, color),
                                 lambda image_base64, desde, hasta: self.generar_pdf(image_base64, desde, hasta, titulo, orientation='landscape'))

        self.page.controls.clear()
        self.page.add(
            ft.Text(titulo, size=24),
            ft.Column([
                self.crear_fila_fecha(desde_field, "Desde"),
                self.crear_fila_fecha(hasta_field, "Hasta")
            ]),
            ft.ElevatedButton("Generar Gráfico", on_click=generar_grafico),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def crear_fila_fecha(self, campo_fecha: ft.TextField, etiqueta: str) -> ft.Row:
        """
        Crea una fila con un campo de fecha y un botón para abrir el calendario.
        :param campo_fecha: El campo de texto donde se mostrará la fecha seleccionada.
        :param etiqueta: La etiqueta que se mostrará junto al campo de fecha.
        :return: Una fila con el campo de fecha y el botón para abrir el calendario.
        """
        return ft.Row([
            campo_fecha,
            ft.ElevatedButton(
                "Seleccionar Fecha",
                on_click=lambda _: self.abrir_calendario(_, campo_fecha),
                icon=ft.icons.CALENDAR_MONTH
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
