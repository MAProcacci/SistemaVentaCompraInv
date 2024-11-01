# reportes.py
import flet as ft
from datetime import datetime
from reporte_productos import listar_productos
from reporte_clientes import listar_clientes
from reporte_proveedores import listar_proveedores
from reporte_ventas import listar_ventas
from reporte_compras import listar_compras
from reporte_devoluciones import listar_devoluciones
from reporte_balance import balance
from nav_reportes_pdf import nav_reportes_pdf_app
from nav_facturas_pdf import nav_facturas_pdf_app
from libreria import BaseApp, FormField, get_db_connection
import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, Frame, LongTable
import subprocess
import platform
from typing import List, Tuple, Optional, Any, Callable

# Constants for repeated texts
TITULO_REPORTES = "Reportes"
COLOR_SNACKBAR = "white"

class ReportesApp(BaseApp):
    """
    Clase principal para la gestión de reportes.

    Attributes:
        page (ft.Page): Página de la aplicación.
        main_menu_callback (callable): Función de devolución de llamada para volver al menú principal.
        reportes_dir_pdf (str): Directorio donde se guardan los reportes PDF.
        reportes_dir_csv (str): Directorio donde se guardan los reportes CSV.
        facturas_dir (str): Directorio donde se guardan las facturas PDF.
    """
    def __init__(self, page: ft.Page, main_menu_callback: callable):
        super().__init__(page, main_menu_callback)
        self.reportes_dir_pdf = os.path.join(os.getcwd(), 'Reportes_PDF')
        self.reportes_dir_csv = os.path.join(os.getcwd(), 'Reportes_CSV')
        self.facturas_dir = os.path.join(os.getcwd(), 'facturas')
        os.makedirs(self.reportes_dir_csv, exist_ok=True)
        os.makedirs(self.reportes_dir_pdf, exist_ok=True)

    def main_menu(self):
        """
        Muestra el menú principal de reportes.
        """
        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_REPORTES, size=24),
            ft.ElevatedButton("Productos", on_click=lambda _: listar_productos(self)),
            ft.ElevatedButton("Clientes", on_click=lambda _: listar_clientes(self)),
            ft.ElevatedButton("Proveedores", on_click=lambda _: listar_proveedores(self)),
            ft.ElevatedButton("Ventas", on_click=lambda _: self._open_report_menu("Ventas", listar_ventas)),
            ft.ElevatedButton("Compras", on_click=lambda _: self._open_report_menu("Compras", listar_compras)),
            ft.ElevatedButton("Devoluciones", on_click=lambda _: self._open_report_menu("Devoluciones", listar_devoluciones)),
            ft.ElevatedButton("Balances", on_click=lambda _: self._open_report_menu("Balances", balance)),
            ft.ElevatedButton("Navegar en Reportes PDF", on_click=lambda _: self.navegar_reportes_pdf()),
            ft.ElevatedButton("Navegar en Facturas PDF", on_click=lambda _: self.navegar_facturas_pdf()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def _open_report_menu(self, titulo: str, reporte_func: callable):
        """
        Abre el menú para generar un reporte específico.

        Args:
            titulo (str): Título del reporte.
            reporte_func (callable): Función que genera el reporte.
        """
        desde_field = ft.TextField(label="Desde", hint_text="YYYY-MM-DD", value=datetime.today().strftime('%Y-%m-%d'))
        hasta_field = ft.TextField(label="Hasta", hint_text="YYYY-MM-DD", value=datetime.today().strftime('%Y-%m-%d'))

        def generar_reporte(e):
            desde, hasta = desde_field.value, hasta_field.value
            if self._validar_fechas(desde, hasta):
                reporte_func(self, desde, hasta)

        def filtrar_reporte(e):
            self._mostrar_opciones_filtro(titulo, desde_field.value, hasta_field.value)

        self.page.controls.clear()
        self.page.add(
            ft.Text(titulo, size=24),
            ft.Column([
                self._crear_fila_fecha(desde_field, "Desde"),
                self._crear_fila_fecha(hasta_field, "Hasta")
            ]),
            ft.ElevatedButton("Generar Reporte", on_click=generar_reporte),
            ft.ElevatedButton("Filtrar", on_click=filtrar_reporte),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def _crear_fila_fecha(self, campo_fecha: ft.TextField, etiqueta: str) -> ft.Row:
        """
        Crea una fila con un campo de fecha y un botón para abrir el calendario.

        Args:
            campo_fecha (ft.TextField): Campo de texto para la fecha.
            etiqueta (str): Etiqueta de la fila.

        Returns:
            ft.Row: Fila con el campo de fecha y el botón.
        """
        return ft.Row([
            campo_fecha,
            ft.ElevatedButton(
                "Seleccionar Fecha",
                on_click=lambda _: self.abrir_calendario(_, campo_fecha),
                icon=ft.icons.CALENDAR_MONTH
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def navegar_reportes_pdf(self):
        """
        Navega a la interfaz de gestión de reportes PDF.
        """
        nav_reportes_pdf_app(self.page, self.reportes_dir_pdf, self.main_menu_callback)

    def navegar_facturas_pdf(self):
        """
        Navega a la interfaz de gestión de facturas PDF.
        """
        nav_facturas_pdf_app(self.page, self.facturas_dir, self.main_menu_callback)

    def generar_csv_reporte(self, titulo: str, elementos: List[Any]):
        """
        Genera un archivo CSV con los datos del reporte.

        Args:
            titulo (str): Título del reporte.
            elementos (List[Any]): Lista de elementos a incluir en el reporte.
        """
        nombre_archivo = f"{titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        encabezados, datos = self._obtener_datos_reporte(titulo, elementos)

        ruta_archivo = self.generar_csv(nombre_archivo, encabezados, datos)
        mensaje = f"Archivo CSV generado: {ruta_archivo}" if ruta_archivo else "Error al generar el archivo CSV"

        self.mostrar_mensaje(mensaje, "green")  # Añade el color aquí

    def generar_pdf_reporte(self, titulo: str, elementos: List[Any]):
        """
        Genera un archivo PDF con los datos del reporte.

        Args:
            titulo (str): Título del reporte.
            elementos (List[Any]): Lista de elementos a incluir en el reporte.
        """
        nombre_archivo = f"{titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_archivo = os.path.join(self.reportes_dir_pdf, nombre_archivo)

        # Crear el documento PDF
        doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []
        encabezados, datos = self._obtener_datos_reporte(titulo, elementos)
        data = self._crear_data_para_pdf(encabezados, datos, styles)

        table = LongTable(data, repeatRows=1)
        table.setStyle(self._crear_estilo_tabla())

        elements.append(table)

        # Construir el documento con el encabezado
        doc.build(elements, onFirstPage=self._encabezado_pdf(titulo), onLaterPages=self._encabezado_pdf(titulo))

        mensaje = f"Archivo PDF generado: {ruta_archivo}"
        self.mostrar_mensaje(mensaje, "green")  # Añade el color aquí
        self.mostrar_confirmacion_imprimir(ruta_archivo)

    def _obtener_datos_reporte(self, titulo: str, elementos: List[Any]) -> Tuple[List[str], List[List[Any]]]:
        """
        Obtiene los encabezados y datos para el reporte.

        Args:
            titulo (str): Título del reporte.
            elementos (List[Any]): Lista de elementos a incluir en el reporte.

        Returns:
            Tuple[List[str], List[List[Any]]]: Encabezados y datos del reporte.
        """
        if "Productos" in titulo:
            encabezados = ["ID", "Nombre", "Stock", "Precio Venta", "Precio Costo"]
            datos = [[e.controls[1].value, e.controls[3].value, e.controls[5].value, e.controls[7].value,
                      e.controls[9].value] for e in elementos if len(e.controls) >= 10]
        elif "Clientes" in titulo or "Proveedores" in titulo:
            encabezados = ["ID", "Nombre", "Teléfono", "Email"]
            datos = [[e.controls[1].value, e.controls[3].value, e.controls[5].value, e.controls[7].value] for e in
                     elementos if len(e.controls) >= 8]
        elif "Ventas" in titulo:
            encabezados = ["Factura ID", "Cliente", "Producto", "Cantidad", "Precio", "Fecha"]
            datos = [[e.controls[1].value, e.controls[5].value, e.controls[7].value, e.controls[9].value,
                      e.controls[11].value, e.controls[3].value] for e in elementos if len(e.controls) >= 12]
        elif "Compras" in titulo:
            encabezados = ["Nro Referencia", "Proveedor", "Producto", "Cantidad", "Fecha", "Precio Costo"]
            datos = [[e.controls[1].value, e.controls[3].value, e.controls[5].value, e.controls[7].value,
                      e.controls[9].value, e.controls[11].value] for e in elementos if len(e.controls) >= 12]
        elif "Devoluciones" in titulo:
            encabezados = ["Factura ID", "Cliente", "Producto", "Cantidad", "Fecha"]
            datos = [[e.controls[1].value, e.controls[3].value, e.controls[5].value, e.controls[7].value,
                      e.controls[9].value] for e in elementos if len(e.controls) >= 10]
        else:
            encabezados, datos = [], []
        return encabezados, datos

    def _crear_data_para_pdf(self, encabezados: List[str], datos: List[List[Any]], styles) -> List[List[Paragraph]]:
        """
        Crea los datos para el PDF en formato de párrafos.

        Args:
            encabezados (List[str]): Lista de encabezados.
            datos (List[List[Any]]): Lista de datos.
            styles: Hoja de estilos para el PDF.

        Returns:
            List[List[Paragraph]]: Datos en formato de párrafos.
        """
        estilo_encabezado = ParagraphStyle(
            'encabezado',
            parent=styles['Normal'],
            fontSize=7,
            leading=8,
            alignment=1,
            wordWrap='CJK',
            fontName='Helvetica-Bold',
            textColor=colors.whitesmoke
        )

        estilo_datos = ParagraphStyle(
            'datos',
            parent=styles['Normal'],
            fontSize=7,
            leading=7,
            alignment=1,
            wordWrap='CJK'
        )

        encabezados_paragraph = [Paragraph(str(header), estilo_encabezado) for header in encabezados]
        datos_paragraph = [[Paragraph(str(cell), estilo_datos) for cell in row] for row in datos]

        return [encabezados_paragraph] + datos_paragraph

    def _crear_estilo_tabla(self) -> TableStyle:
        """
        Crea el estilo de la tabla para el PDF.

        Returns:
            TableStyle: Estilo de la tabla.
        """
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ])

    def _encabezado_pdf(self, titulo: str) -> Callable:
        """
        Crea el encabezado para el PDF.

        Args:
            titulo (str): Título del reporte.

        Returns:
            Callable: Función que dibuja el encabezado en el PDF.
        """
        def encabezado(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica-Bold', 16)
            width, height = letter
            text_width = canvas.stringWidth(titulo, 'Helvetica-Bold', 16)
            x_position = (width - text_width) / 2
            canvas.drawString(x_position, 750, titulo)
            canvas.setFont('Times-Roman', 10)
            canvas.drawRightString(letter[0] - 30, 750, f"Página {doc.page}")
            canvas.restoreState()
        return encabezado

    def mostrar_confirmacion_imprimir(self, ruta_pdf: str):
        """
        Muestra un diálogo de confirmación para imprimir el PDF.

        Args:
            ruta_pdf (str): Ruta del archivo PDF a imprimir.
        """
        def imprimir(_):
            self.imprimir_pdf(ruta_pdf)
            self.page.dialog.open = False
            self.page.update()

        def cancelar(_):
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Imprimir Reporte"),
            content=ft.Text("¿Desea imprimir el reporte?"),
            actions=[
                ft.TextButton("Sí", on_click=imprimir),
                ft.TextButton("No", on_click=cancelar)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def imprimir_pdf(self, ruta_pdf: str):
        """
        Imprime el archivo PDF.

        Args:
            ruta_pdf (str): Ruta del archivo PDF a imprimir.
        """
        try:
            if os.name == 'nt':  # Windows
                sumatra_path = r"C:\Users\Owner\AppData\Local\SumatraPDF\SumatraPDF.exe"
                subprocess.run([sumatra_path, '-print-to-default', ruta_pdf], shell=True, check=True)
            elif os.name == 'posix':  # macOS o Linux
                if platform.system() == 'Darwin':  # macOS
                    subprocess.run(['lpr', ruta_pdf], check=True)
                else:  # Linux
                    subprocess.run(['lp', ruta_pdf], check=True)
            else:
                raise OSError("Sistema operativo no soportado para imprimir")
        except Exception as e:
            self.guardar_error(str(e))
            self.mostrar_mensaje(f"Error al imprimir: {str(e)}", "red")  # Añade el color aquí

    def guardar_error(self, mensaje_error: str):
        """
        Guarda un mensaje de error en un archivo de texto.

        Args:
            mensaje_error (str): Mensaje de error a guardar.
        """
        ruta_errores = os.path.join(os.getcwd(), 'errores')
        os.makedirs(ruta_errores, exist_ok=True)

        fecha_hora = datetime.now().strftime("%m%d%y_%H%M")
        nombre_archivo = f"Error_{fecha_hora}.txt"
        ruta_archivo = os.path.join(ruta_errores, nombre_archivo)

        with open(ruta_archivo, 'w') as archivo:
            archivo.write(mensaje_error)

    def generar_csv(self, nombre_archivo: str, encabezados: List[str], datos: List[List[Any]]) -> Optional[str]:
        """
        Genera un archivo CSV.

        Args:
            nombre_archivo (str): Nombre del archivo CSV.
            encabezados (List[str]): Lista de encabezados.
            datos (List[List[Any]]): Lista de datos.

        Returns:
            Optional[str]: Ruta del archivo CSV generado, o None si hubo un error.
        """
        ruta_archivo = os.path.join(self.reportes_dir_csv, nombre_archivo)
        try:
            with open(ruta_archivo, 'w', newline='', encoding='utf-8') as archivo_csv:
                writer = csv.writer(archivo_csv)
                writer.writerow(encabezados)
                writer.writerows(datos)
            return ruta_archivo
        except Exception as e:
            print(f"Error al generar el archivo CSV: {str(e)}")
            return None

def reportes_app(page: ft.Page, main_menu_callback: callable):
    """
    Función principal para iniciar la aplicación de reportes.

    Args:
        page (ft.Page): Página de la aplicación.
        main_menu_callback (callable): Función de devolución de llamada para volver al menú principal.
    """
    app = ReportesApp(page, main_menu_callback)
    app.main_menu()



