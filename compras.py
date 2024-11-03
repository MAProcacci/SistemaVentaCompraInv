# compras.py
import flet as ft
from typing import List, Tuple, Optional
from models import Compra, Producto, Proveedor
from database import create_connection
import datetime
from libreria import BaseApp, FormField


class ComprasApp(BaseApp):
    """
    Clase que representa la aplicación de compras.
    """
    def __init__(self, page: ft.Page, main_menu_callback):
        super().__init__(page, main_menu_callback)
        self.proveedor_field = ft.TextField(label="Proveedor",
                                            read_only=True,
                                            width=500,
                                            border_color=ft.colors.OUTLINE,
                                            disabled=True)

        self.nro_referencia_field = ft.TextField(label="Número de Referencia", width=200)
        self.carrito: List[Tuple[int, str, int, float]] = []
        self.total_compra: float = 0

    def listar_proveedores(self):
        """
        Muestra una lista de proveedores en la aplicación.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Proveedores")
            proveedores = cursor.fetchall()

        def filtrar_proveedores(e):
            """
            Filtra la lista de proveedores según el texto ingresado en el campo de filtro.
            """
            filtro = filtro_field.value.lower()
            proveedores_filtrados = [proveedor for proveedor in proveedores if
                                     filtro in str(proveedor[0]).lower() or filtro in proveedor[1].lower()]
            actualizar_lista_proveedores(proveedores_filtrados)

        def seleccionar_proveedor(e):
            """
            Selecciona un proveedor de la lista y actualiza el campo de proveedor en la aplicación.
            """
            proveedor_id, proveedor_nombre = e.control.data
            self.proveedor_field.value = f"{proveedor_id} - {proveedor_nombre}"
            self.page.update()
            self.main_menu()

        def actualizar_lista_proveedores(proveedores_filtrados):
            """
            Actualiza la lista de proveedores en la aplicación.
            :param proveedores_filtrados: Lista de proveedores filtrados.
            """
            proveedor_list.controls.clear()
            for proveedor in proveedores_filtrados:
                proveedor_list.controls.append(
                    ft.ElevatedButton(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"Nombre: ", color="blue"),
                                ft.Text(f"{proveedor[1]}", weight=ft.FontWeight.BOLD, color="white"),
                                ft.Text(f"Teléfono: ", color="blue"),
                                ft.Text(f"{proveedor[2]}", weight=ft.FontWeight.BOLD, color="white")
                            ], alignment=ft.MainAxisAlignment.CENTER),
                        ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        on_click=seleccionar_proveedor,
                        data=(proveedor[0], proveedor[1])
                    )
                )
            self.page.update()

        self.page.controls.clear()
        self.page.add(ft.Text("Seleccionar Proveedor", size=24))

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_proveedores, width=500,
                                    border_color=ft.colors.OUTLINE)

        proveedor_list = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        actualizar_lista_proveedores(proveedores)

        self.page.add(
            filtro_field,
            ft.Container(
                content=proveedor_list,
                height=400,
                width=600,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=ft.border_radius.all(10),
            ),
            ft.ElevatedButton("Volver", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def listar_productos(self):
        """
        Muestra una lista de productos en la aplicación.
        """
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Productos")
            productos = cursor.fetchall()

            for i, producto in enumerate(productos):
                cursor.execute("""
                    SELECT precio_costo
                    FROM Compras
                    WHERE producto_id = ?
                    ORDER BY fecha DESC
                    LIMIT 1
                """, (producto[0],))
                precio_costo = cursor.fetchone()
                productos[i] += (precio_costo[0] if precio_costo else None,)

        def filtrar_productos(e):
            """
            Filtra la lista de productos según el texto ingresado en el campo de filtro.
            """
            filtro = filtro_field.value.lower()
            productos_filtrados = [producto for producto in productos if
                                   filtro in str(producto[0]).lower() or filtro in producto[1].lower()]
            actualizar_lista_productos(productos_filtrados)

        def agregar_al_carrito(e):
            """
            Agrega un producto al carrito de compras.
            """
            # Asegúrate de que e.control.data contiene los 6 valores esperados
            producto_id, producto_nombre, _, _, _, ultimo_precio_costo = e.control.data

            # Asegúrate de que estás capturando el campo de cantidad correctamente
            cantidad_field = None
            precio_costo_field = None
            for control in e.control.parent.controls:
                if isinstance(control, ft.TextField) and control.label == "Cantidad":
                    cantidad_field = control
                elif isinstance(control, ft.TextField) and control.label == "Precio Costo":
                    precio_costo_field = control

            if cantidad_field is None or precio_costo_field is None:
                self.mostrar_mensaje("Error: Campos de cantidad o precio de costo no encontrados", "red")
                return

            try:
                cantidad = int(cantidad_field.value)
                precio_costo = float(precio_costo_field.value)

                if cantidad <= 0 or precio_costo <= 0:
                    raise ValueError("La cantidad y el precio de costo deben ser números positivos")

            except ValueError:
                self.mostrar_mensaje("Error: La cantidad y el precio de costo deben ser números positivos", "red")
                return

            self.carrito.append((producto_id, producto_nombre, cantidad, precio_costo))
            self.total_compra += cantidad * precio_costo
            self.mostrar_mensaje(f"Agregado al carrito: {producto_nombre} x{cantidad}", "green")
            self.actualizar_vista_carrito()

        def actualizar_lista_productos(productos_filtrados):
            """
            Actualiza la lista de productos en la vista.
            :param productos_filtrados: Lista de productos filtrados.
            """
            producto_list.controls.clear()
            for producto in productos_filtrados:
                ultimo_precio_costo = producto[5] if producto[5] is not None else "N/A"
                producto_row = ft.Row([
                    ft.Text(f"Nombre: ", color="blue"),
                    ft.Text(f"{producto[1]}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Stock: ", color="blue"),
                    ft.Text(f"{producto[4]}", weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"Último Precio Costo: $", color="blue"),
                    ft.Text(f"{float(ultimo_precio_costo) if ultimo_precio_costo != 'N/A' else 'N/A'}",
                            weight=ft.FontWeight.BOLD, color="white"),
                    ft.TextField(label="Cantidad", value="1", width=100),
                    ft.TextField(label="Precio Costo", value=str(ultimo_precio_costo), width=100),
                    ft.ElevatedButton(
                        "Agregar al carrito",
                        on_click=agregar_al_carrito,
                        data=(producto[0], producto[1], producto[2], producto[3], producto[4], ultimo_precio_costo)
                    )
                ])

                producto_list.controls.append(producto_row)
            self.page.update()

        self.page.controls.clear()
        self.page.add(ft.Text("Seleccionar Productos", size=24))

        filtro_field = ft.TextField(label="Filtrar por ID o Nombre", on_change=filtrar_productos, width=500,
                                    border_color=ft.colors.OUTLINE)

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
        """
        Actualiza la vista del carrito de compras.
        :return: Una tupla que contiene la vista del carrito y el texto que muestra el total de la compra.
        """
        carrito_container = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        for index, item in enumerate(self.carrito):
            producto_id, producto_nombre, cantidad, precio_costo = item
            item_row = ft.Row([
                ft.Text(f"{producto_nombre}"),
                ft.TextField(value=str(cantidad), width=50,
                             on_change=lambda e, i=index: self.modificar_cantidad(e, i)),
                ft.TextField(value=str(precio_costo), width=100,
                             on_change=lambda e, i=index: self.modificar_precio_costo(e, i)),
                ft.Text(f"${precio_costo:.2f}"),
                ft.IconButton(ft.icons.EDIT, on_click=lambda _, i=index: self.editar_producto(i)),
                ft.IconButton(ft.icons.DELETE, on_click=lambda _, i=index: self.eliminar_producto(i))
            ])
            carrito_container.controls.append(item_row)

        total_text = ft.Text(f"Total de la compra: ${self.total_compra:.2f}")
        return carrito_container, total_text

    def modificar_cantidad(self, e, index: int):
        """
        Modifica la cantidad de un producto en el carrito.
        :param e: Evento de cambio en el campo de cantidad.
        :param index: Índice del producto en el carrito.
        :return: None
        """
        try:
            nueva_cantidad = int(e.control.value)
            if nueva_cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")

            producto_id, producto_nombre, _, precio_costo = self.carrito[index]
            self.carrito[index] = (producto_id, producto_nombre, nueva_cantidad, precio_costo)
            self.actualizar_total()
            self.actualizar_vista_carrito()
        except ValueError:
            e.control.value = str(self.carrito[index][2])
            self.page.update()

    def modificar_precio_costo(self, e, index: int):
        """
        Modifica el precio de costo de un producto en el carrito.
        :param e: Evento de cambio en el campo de precio de costo.
        :param index: Índice del producto en el carrito.
        :return: None
        """
        try:
            nuevo_precio_costo = float(e.control.value)
            if nuevo_precio_costo <= 0:
                raise ValueError("El precio de costo debe ser positivo")

            producto_id, producto_nombre, cantidad, _ = self.carrito[index]
            self.carrito[index] = (producto_id, producto_nombre, cantidad, nuevo_precio_costo)
            self.actualizar_total()
            self.actualizar_vista_carrito()
        except ValueError:
            e.control.value = str(self.carrito[index][3])
            self.page.update()

    def eliminar_producto(self, index: int):
        """
        Elimina un producto del carrito.
        :param index: Índice del producto en el carrito.
        :return: None
        """
        del self.carrito[index]
        self.actualizar_total()
        self.actualizar_vista_carrito()

    def editar_producto(self, index: int):
        """
        Edita un producto en el carrito.
        :param index: Índice del producto en el carrito.
        :return: None
        """
        producto_id, producto_nombre, cantidad, precio_costo = self.carrito[index]
        cantidad_field = ft.TextField(label="Nueva Cantidad", value=str(cantidad), width=100)
        precio_costo_field = ft.TextField(label="Nuevo Precio Costo", value=str(precio_costo), width=100)

        def guardar_cambios(_):
            """
            Guarda los cambios realizados en el producto.
            :param _: Evento de clic en el botón de guardar cambios.
            :return: None
            """
            try:
                nueva_cantidad = int(cantidad_field.value)
                nuevo_precio_costo = float(precio_costo_field.value)
                if nueva_cantidad <= 0 or nuevo_precio_costo <= 0:
                    raise ValueError("La cantidad y el precio de costo deben ser positivos")

                self.carrito[index] = (producto_id, producto_nombre, nueva_cantidad, nuevo_precio_costo)
                self.actualizar_total()
                self.mostrar_mensaje("Cantidad y precio de costo actualizados", "green")
                self.actualizar_vista_carrito()
                self.main_menu()

            except ValueError:
                self.mostrar_mensaje("Error: La cantidad y el precio de costo deben ser números positivos", "red")

        self.page.controls.clear()
        self.page.add(
            ft.Text("Editar Producto", size=24),
            ft.Text(f"Producto: {producto_nombre}"),
            cantidad_field,
            precio_costo_field,
            ft.ElevatedButton("Guardar Cambios", on_click=guardar_cambios),
            ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu())
        )
        self.page.update()

    def actualizar_total(self):
        """
        Actualiza el total de la compra.
        :return: None
        """
        self.total_compra = sum(item[2] * item[3] for item in self.carrito)

    def actualizar_vista_carrito(self):
        """
        Actualiza la vista del carrito.
        :return: None
        """
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
        """
        Muestra el menú principal.
        :return: None
        """
        def finalizar_compra(_):
            """
            Finaliza la compra.
            :param _: Evento de clic en el botón de finalizar compra.
            :return: None
            """
            if not self.proveedor_field.value or not self.carrito:
                self.mostrar_mensaje("Error: Seleccione un proveedor y al menos un producto", "red")
                return

            try:
                proveedor_id = int(self.proveedor_field.value.split(' - ')[0])
            except (ValueError, AttributeError, IndexError):
                self.mostrar_mensaje("Error: Proveedor no seleccionado correctamente", "red")
                return

            nro_referencia = self.nro_referencia_field.value
            if not nro_referencia:
                self.mostrar_mensaje("Error: Ingrese un número de referencia", "red")
                return

            fecha = datetime.datetime.now().strftime("%Y-%m-%d")

            with create_connection() as conn:
                cursor = conn.cursor()
                try:
                    for producto_id, producto_nombre, cantidad, precio_costo in self.carrito:
                        nueva_compra = Compra(
                            proveedor_id=proveedor_id,
                            producto_id=producto_id,
                            cantidad=cantidad,
                            fecha=fecha,
                            precio_costo=precio_costo,
                            nro_referencia=nro_referencia
                        )
                        nueva_compra.save(cursor)

                        cursor.execute("SELECT stock FROM Productos WHERE id=?", (producto_id,))
                        stock_result = cursor.fetchone()

                        if stock_result is None:
                            raise ValueError(f"Error: Producto con ID {producto_id} no encontrado")

                        cursor.execute("UPDATE Productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))

                    conn.commit()
                    self.mostrar_mensaje("Compra finalizada con éxito", "green")
                except Exception as e:
                    conn.rollback()
                    self.mostrar_mensaje(f"Error: {str(e)}", "red")

            self.proveedor_field.value = ""
            self.nro_referencia_field.value = ""
            self.carrito = []
            self.total_compra = 0
            self.actualizar_vista_carrito()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Gestión de Compras", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            self.proveedor_field,
            self.nro_referencia_field,
            ft.ElevatedButton("Seleccionar Proveedor", on_click=lambda _: self.listar_proveedores()),
            ft.ElevatedButton("Seleccionar Productos", on_click=lambda _: self.listar_productos()),
        )

        carrito_container, total_text = self.actualizar_carrito()
        carrito_container.data = "carrito_container"
        total_text.data = "total_text"
        self.page.add(carrito_container, total_text)

        self.page.add(
            ft.ElevatedButton("Finalizar Compra", on_click=finalizar_compra),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )

        self.page.update()


def compras_app(page: ft.Page, main_menu_callback):
    """
    Funcion principal de la aplicacion
    :param page: Pagina de la aplicacion
    :param main_menu_callback: Callback para volver al menú principal
    :return: None
    """
    app = ComprasApp(page, main_menu_callback)
    app.main_menu()

