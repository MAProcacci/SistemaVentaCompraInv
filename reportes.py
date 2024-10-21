# reportes.py
import flet as ft
from datetime import datetime
from database import create_connection
import csv
import os
from typing import List, Tuple, Optional, Any
from contextlib import contextmanager
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageTemplate, Frame, LongTable
import subprocess
import platform
from nav_reportes_pdf import nav_reportes_pdf_app

# Constants for repeated texts
TITULO_REPORTES = "Reportes"
TITULO_PRODUCTOS = "Reporte de Productos"
TITULO_CLIENTES = "Reporte de Clientes"
TITULO_PROVEEDORES = "Reporte de Proveedores"
TITULO_VENTAS = "Reporte de Ventas"
TITULO_COMPRAS = "Reporte de Compras"
TITULO_BALANCE = "Balance"
TITULO_DEVOLUCIONES = "Reporte de Devoluciones"
COLOR_SNACKBAR = "white"

# ================================================
# Clase Base para Reportes
# ================================================
class ReporteBase:
    """Clase base para reportes. Define la interfaz común."""
    def __init__(self, directory: str):
        self.directory = directory

    def generar_pdf(self, titulo: str, datos: List[List[str]]) -> str:
        """Genera un archivo PDF."""
        nombre_archivo = f"{titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(self.directory, nombre_archivo)
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()

        # Definir el encabezado
        def encabezado(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica-Bold', 12)
            canvas.drawString(30, 750, titulo)
            canvas.restoreState()

        # Crear un PageTemplate con el encabezado
        encabezado_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='encabezado_frame')
        encabezado_template = PageTemplate(id='encabezado_template', frames=[encabezado_frame], onPage=encabezado)
        doc.addPageTemplates([encabezado_template])

        elements = []
        elements.append(self._crear_tabla(datos))
        doc.build(elements)
        return pdf_path

    def _crear_tabla(self, datos: List[List[str]]) -> Table:
        """Crea una tabla PDF a partir de datos."""
        tabla = Table(datos)
        estilos = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        tabla.setStyle(estilos)
        return tabla

# ================================================
# Clase para Reportes
# ================================================
class Reporte(ReporteBase):
    def __init__(self, tipo: str, directory: str):
        super().__init__(directory)
        self.tipo = tipo

    def generar_pdf(self, titulo: str, datos: List[List[str]]) -> str:
        return super().generar_pdf(titulo, datos)

# ================================================
# Fábrica de Reportes
# ================================================
class FabricaReportes:
    """Fábrica para la creación de reportes."""
    @staticmethod
    def crear_reporte(tipo: str, directory: str) -> ReporteBase:
        return Reporte(tipo, directory)

# ================================================
# Mixin para Generación de CSV
# ================================================
class CSVGeneratorMixin:
    def generar_csv(self, nombre_archivo: str, encabezados: List[str], datos: List[List[Any]]) -> Optional[str]:
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

# ================================================
# Clase Principal de la Aplicación
# ================================================
class ReportesApp(CSVGeneratorMixin):
    def __init__(self, page: ft.Page, main_menu_callback: callable):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.reportes_dir_pdf = os.path.join(os.getcwd(), 'Reportes_PDF')
        self.reportes_dir_csv = os.path.join(os.getcwd(), 'Reportes_CSV')
        os.makedirs(self.reportes_dir_csv, exist_ok=True)
        os.makedirs(self.reportes_dir_pdf, exist_ok=True)

    @contextmanager
    def db_connection(self):
        conn = create_connection()
        try:
            yield conn
        finally:
            conn.close()

    def _crear_list_view(self, elementos: List[Any]) -> ft.ListView:
        return ft.ListView(expand=True, spacing=10, controls=elementos)

    def _agregar_reporte(self, titulo: str, elementos: List[Any], desde: Optional[str] = None,
                         hasta: Optional[str] = None):
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
        list_view = self._crear_list_view(elementos)
        column.controls.append(list_view)
        self.page.add(ft.Container(content=column, expand=True))

        self.page.add(ft.ElevatedButton("Generar CSV", on_click=lambda _: self.generar_csv_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Generar PDF", on_click=lambda _: self.generar_pdf_reporte(titulo, elementos)))
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def generar_csv_reporte(self, titulo: str, elementos: List[Any]):
        nombre_archivo = f"{titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        encabezados, datos = self._obtener_datos_reporte(titulo, elementos)

        ruta_archivo = self.generar_csv(nombre_archivo, encabezados, datos)
        mensaje = f"Archivo CSV generado: {ruta_archivo}" if ruta_archivo else "Error al generar el archivo CSV"

        self.mostrar_mensaje(mensaje)

    def _obtener_datos_reporte(self, titulo: str, elementos: List[Any]) -> Tuple[List[str], List[List[Any]]]:
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

    def generar_pdf_reporte(self, titulo: str, elementos: List[Any]):
        nombre_archivo = f"{titulo.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_archivo = os.path.join(self.reportes_dir_pdf, nombre_archivo)

        # Crear el documento PDF
        doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
        styles = getSampleStyleSheet()

        # Definir el encabezado
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

        elements = []

        # Crear la tabla de datos
        encabezados, datos = self._obtener_datos_reporte(titulo, elementos)

        # Crear un estilo personalizado para los encabezados
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

        # Crear un estilo personalizado para los datos
        estilo_datos = ParagraphStyle(
            'datos',
            parent=styles['Normal'],
            fontSize=7,  # Tamaño de fuente para los datos
            leading=7,  # Ajusta el espaciado entre líneas
            alignment=1,  # Centrado
            wordWrap='CJK'
        )

        # Convertir los encabezados en objetos Paragraph con el estilo de encabezado
        encabezados = [Paragraph(str(header), estilo_encabezado) for header in encabezados]

        # Convertir los datos en objetos Paragraph con el estilo de datos
        datos = [[Paragraph(str(cell), estilo_datos) for cell in row] for row in datos]

        data = [encabezados] + datos

        # Usar LongTable en lugar de Table
        table = LongTable(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),  # Tamaño de fuente para los encabezados
            ('FONTSIZE', (0, 1), (-1, -1), 7),  # Tamaño de fuente para los datos
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))

        elements.append(table)

        # Construir el documento con el encabezado
        doc.build(elements, onFirstPage=encabezado, onLaterPages=encabezado)

        mensaje = f"Archivo PDF generado: {ruta_archivo}"
        self.mostrar_mensaje(mensaje)
        self.mostrar_confirmacion_imprimir(ruta_archivo)

    def mostrar_confirmacion_imprimir(self, ruta_pdf: str):
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
            self.mostrar_mensaje(f"Error al imprimir: {str(e)}", "red")

    def guardar_error(self, mensaje_error: str):
        ruta_errores = os.path.join(os.getcwd(), 'errores')
        os.makedirs(ruta_errores, exist_ok=True)

        fecha_hora = datetime.now().strftime("%m%d%y_%H%M")
        nombre_archivo = f"Error_{fecha_hora}.txt"
        ruta_archivo = os.path.join(ruta_errores, nombre_archivo)

        with open(ruta_archivo, 'w') as archivo:
            archivo.write(mensaje_error)

    def abrir_calendario(self, e, campo_fecha: ft.TextField):
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

    def mostrar_mensaje(self, mensaje: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

    def main_menu(self):
        self.page.controls.clear()
        self.page.add(
            ft.Text(TITULO_REPORTES, size=24),
            ft.ElevatedButton("Productos", on_click=lambda _: self.listar_productos()),
            ft.ElevatedButton("Clientes", on_click=lambda _: self.listar_clientes()),
            ft.ElevatedButton("Proveedores", on_click=lambda _: self.listar_proveedores()),
            ft.ElevatedButton("Ventas", on_click=self._open_ventas),
            ft.ElevatedButton("Compras", on_click=self._open_compras),
            ft.ElevatedButton("Devoluciones", on_click=self._open_devoluciones),
            ft.ElevatedButton("Balances", on_click=self._open_balance),
            ft.ElevatedButton("Navegar en Reportes PDF", on_click=lambda _: self.navegar_reportes_pdf()),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def _open_ventas(self, e):
        self._open_report_menu(TITULO_VENTAS, self.listar_ventas)

    def _open_compras(self, e):
        self._open_report_menu(TITULO_COMPRAS, self.listar_compras)

    def _open_devoluciones(self, e):
        self._open_report_menu(TITULO_DEVOLUCIONES, self.listar_devoluciones)

    def _open_balance(self, e):
        self._open_report_menu(TITULO_BALANCE, self.balance)

    def _open_report_menu(self, titulo: str, reporte_func: callable):
        desde_field = ft.TextField(label="Desde", hint_text="YYYY-MM-DD", value=datetime.today().strftime('%Y-%m-%d'))
        hasta_field = ft.TextField(label="Hasta", hint_text="YYYY-MM-DD", value=datetime.today().strftime('%Y-%m-%d'))

        def generar_reporte(e):
            desde, hasta = desde_field.value, hasta_field.value
            if self._validar_fechas(desde, hasta):
                reporte_func(desde, hasta)

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
        return ft.Row([
            campo_fecha,
            ft.ElevatedButton(
                "Seleccionar Fecha",
                on_click=lambda _: self.abrir_calendario(_, campo_fecha),
                icon=ft.icons.CALENDAR_MONTH
            )
        ], alignment=ft.MainAxisAlignment.CENTER)

    def _validar_fechas(self, desde: str, hasta: str) -> bool:
        try:
            desde_date = datetime.strptime(desde, '%Y-%m-%d')
            hasta_date = datetime.strptime(hasta, '%Y-%m-%d')
            if hasta_date < desde_date:
                raise ValueError("La fecha 'Hasta' no puede ser menor que la fecha 'Desde'.")
            return True
        except ValueError as e:
            self.mostrar_mensaje(f"Error: {str(e)}")
            return False

    def _mostrar_opciones_filtro(self, titulo: str, desde: str, hasta: str):
        opciones_filtro = {
            TITULO_VENTAS: ["Producto", "Cliente"],
            TITULO_COMPRAS: ["Producto", "Proveedor"],
            TITULO_DEVOLUCIONES: ["Producto", "Cliente"],
            TITULO_BALANCE: ["Producto", "Cliente", "Proveedor"]
        }

        self.page.controls.clear()
        self.page.add(
            ft.Text("Filtrar por", size=24),
            ft.Column([
                ft.ElevatedButton(opcion,
                                    on_click=lambda _, o=opcion: self.seleccionar_filtro(_, desde, hasta, o, titulo))
                for opcion in opciones_filtro.get(titulo, [])
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def seleccionar_filtro(self, e, desde: str, hasta: str, tipo_filtro: str, reporte_tipo: str):
        with self.db_connection() as conn:
            cursor = conn.cursor()
            if tipo_filtro == "Producto":
                cursor.execute("SELECT id, nombre FROM Productos")
            elif tipo_filtro == "Cliente":
                cursor.execute("SELECT id, nombre FROM Clientes")
            elif tipo_filtro == "Proveedor":
                cursor.execute("SELECT id, nombre FROM Proveedores")
            opciones = cursor.fetchall()

        def filtrar_opciones(e):
            filtro = filtro_field.value.lower()
            opciones_filtradas = [opcion for opcion in opciones if
                                  filtro in str(opcion[0]).lower() or filtro in opcion[1].lower()]
            actualizar_lista_opciones(opciones_filtradas)

        def actualizar_lista_opciones(opciones_filtradas):
            lista_opciones.controls.clear()
            for opcion in opciones_filtradas:
                lista_opciones.controls.append(
                    ft.ElevatedButton(opcion[1], on_click=lambda _, o=opcion: seleccionar_opcion(_, o[0]))
                )
            self.page.update()

        def seleccionar_opcion(e, opcion_id):
            if reporte_tipo == TITULO_VENTAS:
                self.listar_ventas(desde, hasta, producto_id=opcion_id if tipo_filtro == "Producto" else None,
                                   cliente_id=opcion_id if tipo_filtro == "Cliente" else None)
            elif reporte_tipo == TITULO_COMPRAS:
                self.listar_compras(desde, hasta, producto_id=opcion_id if tipo_filtro == "Producto" else None,
                                    proveedor_id=opcion_id if tipo_filtro == "Proveedor" else None)
            elif reporte_tipo == TITULO_BALANCE:
                self.balance(desde, hasta, producto_id=opcion_id if tipo_filtro == "Producto" else None,
                             cliente_id=opcion_id if tipo_filtro == "Cliente" else None,
                             proveedor_id=opcion_id if tipo_filtro == "Proveedor" else None)
            elif reporte_tipo == TITULO_DEVOLUCIONES:
                self.listar_devoluciones(desde, hasta, producto_id=opcion_id if tipo_filtro == "Producto" else None,
                                         cliente_id=opcion_id if tipo_filtro == "Cliente" else None)

        filtro_field = ft.TextField(label=f"Filtrar por ID o {tipo_filtro}", on_change=filtrar_opciones)
        lista_opciones = ft.ListView(expand=True, spacing=10, padding=20)

        self.page.controls.clear()
        self.page.add(
            ft.Text(f"Seleccionar {tipo_filtro}", size=24),
            filtro_field,
            lista_opciones,
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu())
        )

        actualizar_lista_opciones(opciones)
        self.page.update()

    def listar_productos(self, desde: Optional[str] = None, hasta: Optional[str] = None):
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.nombre, p.stock, p.precio AS precio_venta,
                       (SELECT c.precio_costo
                        FROM Compras c
                        WHERE c.producto_id = p.id
                        ORDER BY c.fecha DESC
                        LIMIT 1) AS precio_costo
                FROM Productos p
            """)
            productos = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("ID:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(producto[0]),
                ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(producto[1]),
                ft.Text("Stock:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(producto[2]),
                ft.Text("Precio Venta:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"${producto[3]:.2f}"),
                ft.Text("Precio Costo:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"${producto[4]:.2f}" if producto[4] else "N/A")
            ], alignment=ft.MainAxisAlignment.CENTER) for producto in productos
        ]
        self._agregar_reporte(TITULO_PRODUCTOS, elementos, desde, hasta)

    def listar_clientes(self, desde: Optional[str] = None, hasta: Optional[str] = None):
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes")
            clientes = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("ID:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(cliente[0]),
                ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(cliente[1]),
                ft.Text("Teléfono:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(cliente[2]),
                ft.Text("Email:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(cliente[3])
            ], alignment=ft.MainAxisAlignment.CENTER) for cliente in clientes
        ]
        self._agregar_reporte(TITULO_CLIENTES, elementos, desde, hasta)

    def listar_proveedores(self, desde: Optional[str] = None, hasta: Optional[str] = None):
        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores")
            proveedores = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("ID:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(proveedor[0]),
                ft.Text("Nombre:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(proveedor[1]),
                ft.Text("Teléfono:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(proveedor[2]),
                ft.Text("Email:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(proveedor[3])
            ], alignment=ft.MainAxisAlignment.CENTER) for proveedor in proveedores
        ]
        self._agregar_reporte(TITULO_PROVEEDORES, elementos, desde, hasta)

    def listar_ventas(self, desde: Optional[str] = None, hasta: Optional[str] = None, producto_id: Optional[int] = None,
                      cliente_id: Optional[int] = None):
        query, params = self._construir_query_ventas(desde, hasta, producto_id, cliente_id)

        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            ventas = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("Factura ID:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(venta[0]),
                ft.Text("Fecha:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(venta[1]),
                ft.Text("Cliente:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(venta[2]),
                ft.Text("Producto:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(venta[3]),
                ft.Text("Cantidad:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(venta[4]),
                ft.Text("Precio:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"${venta[5]:.2f}")
            ], alignment=ft.MainAxisAlignment.CENTER) for venta in ventas
        ]
        self._agregar_reporte(TITULO_VENTAS, elementos, desde, hasta)

    def _construir_query_ventas(self, desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                                cliente_id: Optional[int]) -> Tuple[str, List[Any]]:
        query = """
            SELECT v.factura_id, v.fecha, c.nombre AS cliente_nombre, p.nombre AS producto_nombre, v.cantidad, p.precio
            FROM Ventas v
            JOIN Clientes c ON v.cliente_id = c.id
            JOIN Productos p ON v.producto_id = p.id
        """
        params = []
        where_clauses = []

        if desde and hasta:
            where_clauses.append("v.fecha BETWEEN ? AND ?")
            params.extend([desde, hasta])
        if producto_id:
            where_clauses.append("v.producto_id = ?")
            params.append(producto_id)
        if cliente_id:
            where_clauses.append("v.cliente_id = ?")
            params.append(cliente_id)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        return query, params

    def listar_compras(self, desde: Optional[str] = None, hasta: Optional[str] = None,
                       producto_id: Optional[int] = None, proveedor_id: Optional[int] = None):
        query, params = self._construir_query_compras(desde, hasta, producto_id, proveedor_id)

        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            compras = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("Nro Referencia:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(compra[0]),
                ft.Text("Proveedor:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(compra[1]),
                ft.Text("Producto:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(compra[2]),
                ft.Text("Cantidad:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(compra[3]),
                ft.Text("Fecha:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(compra[4]),
                ft.Text("Precio Costo:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"${compra[5]:.2f}")
            ], alignment=ft.MainAxisAlignment.CENTER) for compra in compras
        ]
        self._agregar_reporte(TITULO_COMPRAS, elementos, desde, hasta)

    def _construir_query_compras(self, desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                                 proveedor_id: Optional[int]) -> Tuple[str, List[Any]]:
        query = """
                            SELECT Compras.nro_referencia, Proveedores.nombre, Productos.nombre, Compras.cantidad, Compras.fecha, Compras.precio_costo
                            FROM Compras
                            JOIN Proveedores ON Compras.proveedor_id = Proveedores.id
                            JOIN Productos ON Compras.producto_id = Productos.id
                        """
        params = []
        where_clauses = []

        if desde and hasta:
            where_clauses.append("Compras.fecha BETWEEN ? AND ?")
            params.extend([desde, hasta])
        if producto_id:
            where_clauses.append("Compras.producto_id = ?")
            params.append(producto_id)
        if proveedor_id:
            where_clauses.append("Compras.proveedor_id = ?")
            params.append(proveedor_id)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        return query, params

    def listar_devoluciones(self, desde: Optional[str] = None, hasta: Optional[str] = None,
                            producto_id: Optional[int] = None, cliente_id: Optional[int] = None):
        query, params = self._construir_query_devoluciones(desde, hasta, producto_id, cliente_id)

        with self.db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            devoluciones = cursor.fetchall()

        elementos = [
            ft.Row([
                ft.Text("Factura ID:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(devolucion[0]),
                ft.Text("Cliente:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(devolucion[4]),
                ft.Text("Producto:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(devolucion[1]),
                ft.Text("Cantidad:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(devolucion[2]),
                ft.Text("Fecha:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(devolucion[3])
            ], alignment=ft.MainAxisAlignment.CENTER) for devolucion in devoluciones
        ]
        self._agregar_reporte(TITULO_DEVOLUCIONES, elementos, desde, hasta)

    def _construir_query_devoluciones(self, desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                                      cliente_id: Optional[int]) -> Tuple[str, List[Any]]:
        query = """
                            SELECT d.factura_id, p.nombre AS producto_nombre, d.cantidad, d.fecha, c.nombre AS cliente_nombre
                            FROM Devoluciones d
                            JOIN Productos p ON d.producto_id = p.id
                            JOIN Clientes c ON d.cliente_id = c.id
                        """
        params = []
        where_clauses = []

        if desde and hasta:
            where_clauses.append("d.fecha BETWEEN ? AND ?")
            params.extend([desde, hasta])
        if producto_id:
            where_clauses.append("d.producto_id = ?")
            params.append(producto_id)
        if cliente_id:
            where_clauses.append("d.cliente_id = ?")
            params.append(cliente_id)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        return query, params

    def balance(self, desde: Optional[str] = None, hasta: Optional[str] = None, producto_id: Optional[int] = None,
                cliente_id: Optional[int] = None, proveedor_id: Optional[int] = None):
        with self.db_connection() as conn:
            cursor = conn.cursor()

            # Verificar si el cliente también es un proveedor
            if cliente_id:
                cursor.execute("SELECT id FROM Proveedores WHERE id = ?", (cliente_id,))
                es_proveedor = cursor.fetchone()
                if not es_proveedor:
                    proveedor_id = None

            # Verificar si el proveedor también es un cliente
            if proveedor_id:
                cursor.execute("SELECT id FROM Clientes WHERE id = ?", (proveedor_id,))
                es_cliente = cursor.fetchone()
                if not es_cliente:
                    cliente_id = None

            # Obtener nombres de producto, cliente y proveedor si están filtrados
            producto_nombre = None
            cliente_nombre = None
            proveedor_nombre = None

            if producto_id:
                cursor.execute("SELECT nombre FROM Productos WHERE id = ?", (producto_id,))
                producto_nombre = cursor.fetchone()[0]

            if cliente_id:
                cursor.execute("SELECT nombre FROM Clientes WHERE id = ?", (cliente_id,))
                cliente_nombre = cursor.fetchone()[0]

            if proveedor_id:
                cursor.execute("SELECT nombre FROM Proveedores WHERE id = ?", (proveedor_id,))
                proveedor_nombre = cursor.fetchone()[0]

            # Calcular el total de ventas
            total_ventas = 0
            if cliente_id or not proveedor_id:
                query = """
                                    SELECT SUM(Ventas.cantidad * Productos.precio)
                                    FROM Ventas
                                    JOIN Productos ON Ventas.producto_id = Productos.id
                                """
                params = []
                if desde and hasta:
                    query += " WHERE Ventas.fecha BETWEEN ? AND ?"
                    params.extend([desde, hasta])
                if producto_id:
                    query += " AND Ventas.producto_id = ?"
                    params.append(producto_id)
                if cliente_id:
                    query += " AND Ventas.cliente_id = ?"
                    params.append(cliente_id)

                cursor.execute(query, params)
                total_ventas = cursor.fetchone()[0] or 0

            # Calcular el total de compras
            total_compras = 0
            if proveedor_id or not cliente_id:
                query = """
                                    SELECT SUM(Compras.cantidad * Compras.precio_costo)
                                    FROM Compras
                                """
                params = []
                if desde and hasta:
                    query += " WHERE Compras.fecha BETWEEN ? AND ?"
                    params.extend([desde, hasta])
                if producto_id:
                    query += " AND Compras.producto_id = ?"
                    params.append(producto_id)
                if proveedor_id:
                    query += " AND Compras.proveedor_id = ?"
                    params.append(proveedor_id)

                cursor.execute(query, params)
                total_compras = cursor.fetchone()[0] or 0

        balance = total_ventas - total_compras

        self.page.controls.clear()
        self.page.add(ft.Text(TITULO_BALANCE, size=24, text_align=ft.TextAlign.CENTER))
        self.page.add(ft.Divider(height=20, color="transparent"))  # Línea en blanco

        if desde and hasta:
            self.page.add(ft.Row([
                ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"{desde}"),
                ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"{hasta}")
            ], alignment=ft.MainAxisAlignment.CENTER))

        if producto_nombre:
            self.page.add(ft.Row([
                ft.Text("Filtrado por Producto:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"{producto_nombre}")
            ], alignment=ft.MainAxisAlignment.CENTER))
        if cliente_nombre:
            self.page.add(ft.Row([
                ft.Text("Filtrado por Cliente:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"{cliente_nombre}")
            ], alignment=ft.MainAxisAlignment.CENTER))
        if proveedor_nombre:
            self.page.add(ft.Row([
                ft.Text("Filtrado por Proveedor:", weight=ft.FontWeight.BOLD, color="blue"),
                ft.Text(f"{proveedor_nombre}")
            ], alignment=ft.MainAxisAlignment.CENTER))

        self.page.add(ft.Row([
            ft.Text("Total de Ventas:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"${total_ventas:.2f}")
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(ft.Row([
            ft.Text("Total de Compras:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"${total_compras:.2f}")
        ], alignment=ft.MainAxisAlignment.CENTER))
        self.page.add(ft.Row([
            ft.Text("Balance:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"${balance:.2f}")
        ], alignment=ft.MainAxisAlignment.CENTER))

        self.page.add(ft.ElevatedButton("Generar CSV",
                                        on_click=lambda _: self.generar_csv_balance(total_ventas, total_compras,
                                                                                    balance, desde, hasta,
                                                                                    producto_nombre, cliente_nombre,
                                                                                    proveedor_nombre)))
        self.page.add(ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu()))
        self.page.update()

    def generar_csv_balance(self, total_ventas, total_compras, balance, desde, hasta, producto_nombre, cliente_nombre,
                            proveedor_nombre):
        nombre_archivo = f"balance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        encabezados = ["Concepto", "Valor"]
        datos = [
            ["Total de Ventas", f"${total_ventas:.2f}"],
            ["Total de Compras", f"${total_compras:.2f}"],
            ["Balance", f"${balance:.2f}"]
        ]

        if desde and hasta:
            datos.insert(0, ["Fecha Inicio", desde])
            datos.insert(1, ["Fecha Final", hasta])

        if producto_nombre:
            datos.insert(0, ["Producto", producto_nombre])
        if cliente_nombre:
            datos.insert(0, ["Cliente", cliente_nombre])
        if proveedor_nombre:
            datos.insert(0, ["Proveedor", proveedor_nombre])

        ruta_archivo = self.generar_csv(nombre_archivo, encabezados, datos)
        if ruta_archivo:
            mensaje = f"Archivo CSV del balance generado: {ruta_archivo}"
        else:
            mensaje = "Error al generar el archivo CSV del balance"

        # Mostrar mensaje de éxito o error
        self.mostrar_mensaje(mensaje)

    def navegar_reportes_pdf(self):
        #from nav_reportes_pdf import nav_reportes_pdf_app
        nav_reportes_pdf_app(self.page, self.reportes_dir_pdf, self.main_menu_callback)

def reportes_app(page: ft.Page, main_menu_callback: callable):
    app = ReportesApp(page, main_menu_callback)
    app.main_menu()





