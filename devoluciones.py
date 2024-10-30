# devoluciones.py
import flet as ft
from typing import List, Tuple, Optional
from database import create_connection
from models import Venta, Producto, Devolucion
import datetime

COLOR_SNACKBAR = "white"

class DevolucionesApp:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.factura_seleccionada: Optional[str] = None
        self.productos_a_devolver: List[Tuple[int, str, int, float]] = []

    def listar_facturas(self):
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT DISTINCT v.factura_id, c.nombre
            FROM Ventas v
            JOIN Clientes c ON v.cliente_id = c.id
            """)
            facturas = cursor.fetchall()

        def filtrar_facturas(e):
            filtro = filtro_field.value.lower()
            facturas_filtradas = [factura for factura in facturas if filtro in factura[0].lower() or filtro in factura[1].lower()]
            actualizar_lista_facturas(facturas_filtradas)

        def seleccionar_factura(e):
            factura_id = e.control.data
            self.factura_seleccionada = factura_id
            self.mostrar_factura(factura_id)

        def actualizar_lista_facturas(facturas_filtradas):
            facturas_list.controls.clear()
            for factura in facturas_filtradas:
                factura_id, cliente_nombre = factura
                facturas_list.controls.append(
                    ft.ElevatedButton(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Factura ID: ", color="blue"),
                                ft.Text(f"{factura_id}", weight=ft.FontWeight.BOLD, color="white"),
                                ft.Text(f"Cliente: ", color="blue"),
                                ft.Text(f"{cliente_nombre}", weight=ft.FontWeight.BOLD, color="white")
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),

                        on_click=seleccionar_factura,
                        data=factura_id
                    )
                )
            self.page.update()

        self.page.controls.clear()
        self.page.add(ft.Text("Seleccionar Factura", size=24))

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre",
                                    on_change=filtrar_facturas,
                                    width=500,
                                    border_color=ft.colors.OUTLINE)

        facturas_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)

        # Inicialmente, mostrar todas las facturas
        actualizar_lista_facturas(facturas)

        self.page.add(
            filtro_field,
            ft.Container(
                content=facturas_list,
                height=400,
                width=600,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def mostrar_factura(self, factura_id: str):
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Ventas WHERE factura_id=?", (factura_id,))
            detalles_factura = cursor.fetchall()

        def agregar_devolucion(e):
            producto_id, producto_nombre, cantidad_vendida, precio = e.control.data
            cantidad_devolver = int(e.control.parent.controls[1].value)

            if cantidad_devolver <= 0 or cantidad_devolver > cantidad_vendida:
                self.mostrar_mensaje("Error: Cantidad inválida", "red")
                return

            self.productos_a_devolver.append((producto_id, producto_nombre, cantidad_devolver, precio))
            self.mostrar_mensaje(f"Agregado para devolución: {producto_nombre} x {cantidad_devolver}", "green")
            self.mostrar_factura(factura_id)

        self.page.controls.clear()
        self.page.add(ft.Text(f"Detalles de la Factura Nro: {factura_id}", size=24))
        self.page.add(ft.Divider(height=20, color="transparent"))

        factura_content = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        with create_connection() as conn:
            cursor = conn.cursor()
            for detalle in detalles_factura:
                producto_id = detalle[2]
                cantidad_vendida = detalle[3]
                cursor.execute("SELECT nombre, precio FROM Productos WHERE id=?", (producto_id,))
                producto_info = cursor.fetchone()
                producto_nombre, precio = producto_info

                producto_row = ft.Row([
                    ft.Text(f"Nombre: ", color="blue"),
                    ft.Text(f"{producto_nombre}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Cantidad Vendida: ", color="blue"),
                    ft.Text(f"{cantidad_vendida}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Precio: $", color="blue"),
                    ft.Text(f"{precio:.2f}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.TextField(label="Cantidad a Devolver", value=str(cantidad_vendida), width=100),
                    ft.ElevatedButton(
                        "Agregar al carrito",
                        on_click=agregar_devolucion,
                        data=(producto_id, producto_nombre, cantidad_vendida, precio)
                    )
                ])

                factura_content.controls.append(producto_row)

        self.page.add(
            ft.Container(
                content=factura_content,
                height=400,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Finalizar Selección", on_click=self.mostrar_resumen_devoluciones),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def mostrar_resumen_devoluciones(self, _):
        if not self.productos_a_devolver:
            self.mostrar_mensaje("Error: No se han seleccionado productos para devolver", "red")
            return

        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT c.nombre
            FROM Ventas v
            JOIN Clientes c ON v.cliente_id = c.id
            WHERE v.factura_id=?
            LIMIT 1
            """, (self.factura_seleccionada,))
            cliente_nombre = cursor.fetchone()[0]

        self.page.controls.clear()
        self.page.add(ft.Text(f"Resumen de Devoluciones", size=24))
        self.page.add(ft.Divider(height=20, color="transparent"))
        self.page.add(ft.Text(f"Factura Nro: {self.factura_seleccionada}", size=18))
        self.page.add(ft.Text(f"Cliente: {cliente_nombre}", size=18))
        self.page.add(ft.Divider(height=20, color="transparent"))

        devoluciones_container = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
        for producto_id, producto_nombre, cantidad_devolver, precio in self.productos_a_devolver:
            item_row = ft.Row([
                ft.Text(f"{producto_nombre}"),
                ft.Text(f"Cantidad: {cantidad_devolver}"),
                ft.Text(f"Precio: ${precio:.2f}"),
            ])
            devoluciones_container.controls.append(item_row)

        self.page.add(
            ft.Container(
                content=devoluciones_container,
                height=400,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Confirmar Devolución", on_click=self.finalizar_devolucion),
            ft.ElevatedButton("Volver", on_click=lambda _: self.mostrar_factura(self.factura_seleccionada))
        )
        self.page.update()

    def finalizar_devolucion(self, _):
        if not self.factura_seleccionada or not self.productos_a_devolver:
            self.mostrar_mensaje("Error: Seleccione una factura y al menos un producto para devolver", "red")
            return

        with create_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT cliente_id FROM Ventas WHERE factura_id = ?
                """, (self.factura_seleccionada,))
                cliente_id = cursor.fetchone()

                if cliente_id is None:
                    raise ValueError("Error: No se encontró el cliente asociado a la factura.")

                cliente_id = cliente_id[0]

                for producto_id, _, cantidad_devolver, _ in self.productos_a_devolver:
                    cursor.execute("SELECT stock FROM Productos WHERE id=?", (producto_id,))
                    stock_result = cursor.fetchone()

                    if stock_result is None:
                        raise ValueError(f"Error: Producto con ID {producto_id} no encontrado")

                    stock = stock_result[0]
                    nuevo_stock = stock + cantidad_devolver
                    cursor.execute("UPDATE Productos SET stock = ? WHERE id = ?", (nuevo_stock, producto_id))

                    fecha_devolucion = datetime.datetime.now().strftime("%Y-%m-%d")
                    devolucion = Devolucion(self.factura_seleccionada, producto_id, cantidad_devolver, fecha_devolucion, cliente_id)
                    devolucion.save(cursor)

                conn.commit()
                self.mostrar_mensaje("Devolución finalizada con éxito", "green")

                self.factura_seleccionada = None
                self.productos_a_devolver = []
                self.main_menu_callback()

            except Exception as e:
                conn.rollback()
                self.mostrar_mensaje(f"Error: {str(e)}", "red")

    def mostrar_mensaje(self, mensaje: str, color: str):
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()

def devoluciones_app(page: ft.Page, main_menu_callback):
    app = DevolucionesApp(page, main_menu_callback)
    app.listar_facturas()
