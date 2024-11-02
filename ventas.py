# ventas.py
import os
import subprocess
import flet as ft
from typing import List, Tuple, Optional
from models import Venta, Producto, Cliente
from database import create_connection
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import platform
from libreria import BaseApp, FormField

FACTURA_DIR = 'facturas'
ERROR_DIR = 'errores'
COLOR_SNACKBAR = "white"
COLOR_ERROR = "red"

def leer_taza_interes(main_app_instance):
    try:
        with open('taza_impuesto.txt', 'r') as archivo:
            contenido = archivo.read().strip()
            taza_interes = float(contenido)
            return taza_interes
    except FileNotFoundError:
        main_app_instance.mostrar_mensaje("Error: El archivo 'taza_impuesto.txt' no fue encontrado.", COLOR_ERROR)
        main_app_instance.guardar_error("Error: El archivo 'taza_impuesto.txt' no fue encontrado.")
        return None
    except ValueError:
        main_app_instance.mostrar_mensaje("Error: El contenido del archivo 'taza_impuesto.txt' no es un número válido.", COLOR_ERROR)
        main_app_instance.guardar_error("Error: El contenido del archivo 'taza_impuesto.txt' no es un número válido.")
        return None

class VentasApp(BaseApp):
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__(page, main_menu_callback)
        self.cliente_field = ft.TextField(label="Cliente",
                                          read_only=True,
                                          width=500,
                                          border_color=ft.colors.OUTLINE,
                                          disabled=True)
        self.descuento_field = ft.TextField(label="Descuento %:", value="0", width=100, border_color=ft.colors.OUTLINE)

        self.carrito: List[Tuple[int, str, int, float]] = []
        self.total_venta: float = 0

    def listar_clientes(self):
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Clientes")
            clientes = cursor.fetchall()

        def filtrar_clientes(e):
            filtro = filtro_field.value.lower()
            clientes_filtrados = [cliente for cliente in clientes if filtro in str(cliente[0]).lower() or filtro in cliente[1].lower()]
            actualizar_lista_clientes(clientes_filtrados)

        def seleccionar_cliente(e):
            cliente_id, cliente_nombre = e.control.data
            self.cliente_field.value = f"{cliente_id} - {cliente_nombre}"
            self.page.update()
            self.main_menu()

        def actualizar_lista_clientes(clientes_filtrados):
            cliente_list.controls.clear()
            for cliente in clientes_filtrados:
                cliente_list.controls.append(
                    ft.ElevatedButton(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Nombre: ", color="blue"),
                                ft.Text(f"{cliente[1]}", weight=ft.FontWeight.BOLD, color="white"),
                                ft.Text(f"Teléfono: ", color="blue"),
                                ft.Text(f"{cliente[2]}", weight=ft.FontWeight.BOLD, color="white")
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        on_click=seleccionar_cliente,
                        data=(cliente[0], cliente[1])
                    )
                )
            self.page.update()

        self.page.controls.clear()
        self.page.add(ft.Text("Seleccionar Cliente", size=24))

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_clientes, width=500, border_color=ft.colors.OUTLINE)

        cliente_list = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        actualizar_lista_clientes(clientes)

        self.page.add(
            filtro_field,
            ft.Container(
                content=cliente_list,
                height=400,
                width=600,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def listar_productos(self):
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Productos")
            productos = cursor.fetchall()

        def filtrar_productos(e):
            filtro = filtro_field.value.lower()
            productos_filtrados = [producto for producto in productos if filtro in str(producto[0]).lower() or filtro in producto[1].lower()]
            actualizar_lista_productos(productos_filtrados)

        def agregar_al_carrito(e):
            producto_id, producto_nombre, producto_precio = e.control.data

            # Asegúrate de que estás capturando el campo de cantidad correctamente
            cantidad_field = None
            for control in e.control.parent.controls:
                if isinstance(control, ft.TextField) and control.label == "Cantidad":
                    cantidad_field = control
                    break

            if cantidad_field is None:
                self.mostrar_mensaje("Error: Campo de cantidad no encontrado", "red")
                return

            try:
                cantidad = int(cantidad_field.value)
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser un número entero positivo")
            except ValueError:
                self.mostrar_mensaje("Error: La cantidad debe ser un número entero positivo", "red")
                return

            with create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT stock FROM Productos WHERE id=?", (producto_id,))
                stock_result = cursor.fetchone()

            if stock_result is None:
                self.mostrar_mensaje(f"Error: Producto con ID {producto_id} no encontrado", "red")
                return

            stock = stock_result[0]
            if cantidad > stock:
                self.mostrar_mensaje(f"Error: No hay suficiente stock para {producto_nombre}", "red")
                return

            self.carrito.append((producto_id, producto_nombre, cantidad, producto_precio))
            self.total_venta += cantidad * producto_precio
            self.mostrar_mensaje(f"Agregado al carrito: {producto_nombre} x {cantidad}", "green")
            self.actualizar_vista_carrito()

        def actualizar_lista_productos(productos_filtrados):
            producto_list.controls.clear()
            for producto in productos_filtrados:
                producto_row = ft.Row([
                    ft.Text(f"Nombre: ", color="blue"),
                    ft.Text(f"{producto[1]}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Stock: ", color="blue"),
                    ft.Text(f"{producto[4]}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Precio: $", color="blue"),
                    ft.Text(f"{producto[3]:.2f}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.TextField(label="Cantidad", value="1", width=100),
                    ft.ElevatedButton(
                        "Agregar al carrito",
                        on_click=agregar_al_carrito,
                        data=(producto[0], producto[1], producto[3])
                    )
                ])
                producto_list.controls.append(producto_row)
            self.page.update()

        self.page.controls.clear()
        self.page.add(ft.Text("Seleccionar Productos", size=24))

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_productos, width=500, border_color=ft.colors.OUTLINE)

        producto_list = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        actualizar_lista_productos(productos)

        self.page.add(
            filtro_field,
            ft.Container(
                content=producto_list,
                height=400,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Finalizar selección", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def actualizar_carrito(self) -> Tuple[ft.ListView, ft.Text]:
        carrito_container = ft.ListView(expand=True, spacing=10)
        for index, item in enumerate(self.carrito):
            producto_id, producto_nombre, cantidad, precio = item
            item_row = ft.Row([
                ft.Text(f"{producto_nombre}"),
                ft.TextField(value=str(cantidad), width=50,
                             on_change=lambda e, i=index: self.modificar_cantidad(e, i)),
                ft.Text(f"${precio:.2f}"),
                ft.IconButton(ft.icons.EDIT, on_click=lambda _, i=index: self.editar_producto(i)),
                ft.IconButton(ft.icons.DELETE, on_click=lambda _, i=index: self.eliminar_producto(i))
            ])
            carrito_container.controls.append(item_row)

        total_text = ft.Text(f"Total de la venta: ${self.total_venta:.2f}")
        return carrito_container, total_text

    def modificar_cantidad(self, e, index: int):
        try:
            nueva_cantidad = int(e.control.value)
            if nueva_cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")

            producto_id, producto_nombre, _, precio = self.carrito[index]
            self.carrito[index] = (producto_id, producto_nombre, nueva_cantidad, precio)
            self.actualizar_total()
            self.actualizar_vista_carrito()
        except ValueError:
            e.control.value = str(self.carrito[index][2])
            self.page.update()

    def eliminar_producto(self, index: int):
        del self.carrito[index]
        self.actualizar_total()
        self.actualizar_vista_carrito()

    def editar_producto(self, index: int):
        producto_id, producto_nombre, cantidad, precio = self.carrito[index]
        cantidad_field = ft.TextField(label="Nueva Cantidad", value=str(cantidad), width=100)

        def guardar_cambios(_):
            try:
                nueva_cantidad = int(cantidad_field.value)
                if nueva_cantidad <= 0:
                    raise ValueError("La cantidad debe ser positiva")

                self.carrito[index] = (producto_id, producto_nombre, nueva_cantidad, precio)
                self.actualizar_total()
                self.mostrar_mensaje("Cantidad actualizada", "green")
                self.actualizar_vista_carrito()
                self.main_menu()

            except ValueError:
                self.mostrar_mensaje("Error: La cantidad debe ser un número positivo", "red")

        self.page.controls.clear()
        self.page.add(
            ft.Text("Editar Producto", size=24),
            ft.Text(f"Producto: {producto_nombre}"),
            cantidad_field,
            ft.ElevatedButton("Guardar Cambios", on_click=guardar_cambios),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def actualizar_total(self):
        self.total_venta = sum(item[2] * item[3] for item in self.carrito)

    def actualizar_vista_carrito(self):
        carrito_container, total_text = self.actualizar_carrito()
        for control in self.page.controls[:]:
            if isinstance(control, ft.ListView) and control.data == "carrito_container":
                self.page.controls.remove(control)
            if isinstance(control, ft.Text) and control.data == "total_text":
                self.page.controls.remove(control)

        carrito_container.data = "carrito_container"
        total_text.data = "total_text"
        self.page.add(carrito_container, total_text)
        self.page.update()

    def main_menu(self):
        def finalizar_venta(_):
            if not self.cliente_field.value or not self.carrito:
                self.mostrar_mensaje("Error: Seleccione un cliente y al menos un producto", "red")
                return

            try:
                cliente_id = int(self.cliente_field.value.split(' - ')[0])
                descuento_porcentaje = float(self.descuento_field.value)
                if descuento_porcentaje < 0 or descuento_porcentaje > 100:
                    raise ValueError("El descuento debe estar entre 0 y 100")
            except (ValueError, AttributeError, IndexError):
                self.mostrar_mensaje("Error: Cliente no seleccionado correctamente o descuento inválido", "red")
                return

            fecha = datetime.datetime.now().strftime("%Y-%m-%d")
            factura_id = self.generar_numero_factura()

            with create_connection() as conn:
                cursor = conn.cursor()
                try:
                    for producto_id, producto_nombre, cantidad, _ in self.carrito:
                        nueva_venta = Venta(
                            cliente_id=cliente_id,
                            producto_id=producto_id,
                            cantidad=cantidad,
                            fecha=fecha,
                            factura_id=factura_id
                        )
                        nueva_venta.save(cursor)

                        cursor.execute("SELECT stock FROM Productos WHERE id=?", (producto_id,))
                        stock_result = cursor.fetchone()

                        if stock_result is None:
                            raise ValueError(f"Error: Producto con ID {producto_id} no encontrado")

                        stock = stock_result[0]
                        if cantidad > stock:
                            raise ValueError(f"Error: No hay suficiente stock para {producto_nombre}")

                        cursor.execute("UPDATE Productos SET stock = stock - ? WHERE id = ?", (cantidad, producto_id))

                    conn.commit()
                    self.mostrar_mensaje(f"Venta finalizada con éxito. Número de factura: {factura_id}", "green")
                    self.generar_factura_pdf(factura_id, cliente_id, fecha, descuento_porcentaje)

                except Exception as e:
                    conn.rollback()
                    self.mostrar_mensaje(f"Error: {str(e)}", "red")

            self.cliente_field.value = ""
            self.descuento_field.value = "0"
            self.carrito = []
            self.total_venta = 0
            self.actualizar_vista_carrito()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Ventas", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            self.cliente_field,
            self.descuento_field,
            ft.ElevatedButton("Seleccionar Cliente", on_click=lambda _: self.listar_clientes()),
            ft.ElevatedButton("Seleccionar Productos", on_click=lambda _: self.listar_productos()),
        )

        carrito_container, total_text = self.actualizar_carrito()
        carrito_container.data = "carrito_container"
        total_text.data = "total_text"
        self.page.add(carrito_container, total_text)

        self.page.add(
            ft.ElevatedButton("Finalizar Venta", on_click=finalizar_venta),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )

        self.page.update()

    def generar_numero_factura(self) -> str:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(factura_id) FROM Ventas")
            max_factura_id = cursor.fetchone()[0]

        if max_factura_id is None:
            return "00000001"
        else:
            try:
                return str(int(max_factura_id) + 1).zfill(8)
            except ValueError:
                return "00000001"

    def generar_factura_pdf(self, factura_id: str, cliente_id: int, fecha: str, descuento_porcentaje: float):
        ruta_facturas = os.path.join(os.getcwd(), FACTURA_DIR)
        os.makedirs(ruta_facturas, exist_ok=True)
        ruta_factura = os.path.join(ruta_facturas, f'factura_{factura_id}.pdf')

        TAX_RATE = leer_taza_interes(self)

        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, telefono, email FROM Clientes WHERE id=?", (cliente_id,))
            cliente_info = cursor.fetchone()

        if cliente_info is None:
            self.mostrar_mensaje("Error: Cliente no encontrado", "red")
            return

        cliente_nombre, cliente_telefono, cliente_email = cliente_info

        doc = SimpleDocTemplate(ruta_factura, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']

        elements.append(Paragraph("Inversiones Torino, C.A.", title_style))
        elements.append(Spacer(1, 12))

        factura_info = [
            ["Nro. Factura:", factura_id],
            ["Fecha:", fecha],
            ["Cliente:", cliente_nombre],
            ["Teléfono:", cliente_telefono],
            ["Email:", cliente_email],
            ["Descuento:", f"{descuento_porcentaje}%"]
        ]
        t = Table(factura_info, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        data = [["Producto", "Cantidad", "Precio", "Total"]]
        total_venta = 0
        for producto_id, producto_nombre, cantidad, precio in self.carrito:
            total = cantidad * precio
            total_venta += total
            data.append([producto_nombre, str(cantidad), f"${precio:.2f}", f"${total:.2f}"])

        t = Table(data, colWidths=[250, 70, 70, 70])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        descuento = total_venta * (descuento_porcentaje / 100)
        total_venta_con_descuento = total_venta - descuento
        impuesto = total_venta_con_descuento * TAX_RATE
        total_con_impuesto = total_venta_con_descuento + impuesto
        data = [
            ["Total de la venta:", f"${total_venta:.2f}"],
            [f"Descuento ({descuento_porcentaje:.2f}%):", f"${descuento:.2f}"],
            ["Total con descuento:", f"${total_venta_con_descuento:.2f}"],
            [f"Impuesto ({TAX_RATE * 100:.2f}%):", f"${impuesto:.2f}"],
            ["Total con impuesto:", f"${total_con_impuesto:.2f}"]
        ]
        t = Table(data, colWidths=[350, 110])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)

        doc.build(elements)

        self.mostrar_mensaje(f"Factura generada en {ruta_factura}", "green")
        self.mostrar_confirmacion_imprimir(ruta_factura)

    def mostrar_confirmacion_imprimir(self, ruta_pdf: str):
        def imprimir(_):
            self.imprimir_pdf(ruta_pdf)
            self.page.dialog.open = False
            self.page.update()

        def cancelar(_):
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Imprimir Factura"),
            content=ft.Text("¿Desea imprimir la factura?"),
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
        ruta_errores = os.path.join(os.getcwd(), ERROR_DIR)
        os.makedirs(ruta_errores, exist_ok=True)

        fecha_hora = datetime.datetime.now().strftime("%m%d%y_%H%M")
        nombre_archivo = f"Error_{fecha_hora}.txt"
        ruta_archivo = os.path.join(ruta_errores, nombre_archivo)

        with open(ruta_archivo, 'w') as archivo:
            archivo.write(mensaje_error)

def ventas_app(page: ft.Page, main_menu_callback):
    app = VentasApp(page, main_menu_callback)
    app.main_menu()
