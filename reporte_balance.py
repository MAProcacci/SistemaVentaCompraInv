# reporte_balance.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection
from datetime import datetime

TITULO_BALANCE = "Balance"

def balance(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None, producto_id: Optional[int] = None,
            cliente_id: Optional[int] = None, proveedor_id: Optional[int] = None):
    """
    Genera y muestra el reporte de balance financiero.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        producto_id (Optional[int]): ID del producto a filtrar. Por defecto es None.
        cliente_id (Optional[int]): ID del cliente a filtrar. Por defecto es None.
        proveedor_id (Optional[int]): ID del proveedor a filtrar. Por defecto es None.
    """
    with get_db_connection() as conn:
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

    app.page.controls.clear()
    app.page.add(ft.Text(TITULO_BALANCE, size=24, text_align=ft.TextAlign.CENTER))
    app.page.add(ft.Divider(height=20, color="transparent"))  # Línea en blanco

    if desde and hasta:
        app.page.add(ft.Row([
            ft.Text("Fecha Inicio:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"{desde}"),
            ft.Text("Fecha Final:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"{hasta}")
        ], alignment=ft.MainAxisAlignment.CENTER))

    if producto_nombre:
        app.page.add(ft.Row([
            ft.Text("Filtrado por Producto:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"{producto_nombre}")
        ], alignment=ft.MainAxisAlignment.CENTER))
    if cliente_nombre:
        app.page.add(ft.Row([
            ft.Text("Filtrado por Cliente:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"{cliente_nombre}")
        ], alignment=ft.MainAxisAlignment.CENTER))
    if proveedor_nombre:
        app.page.add(ft.Row([
            ft.Text("Filtrado por Proveedor:", weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text(f"{proveedor_nombre}")
        ], alignment=ft.MainAxisAlignment.CENTER))

    app.page.add(ft.Row([
        ft.Text("Total de Ventas:", weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text(f"${total_ventas:.2f}")
    ], alignment=ft.MainAxisAlignment.CENTER))
    app.page.add(ft.Row([
        ft.Text("Total de Compras:", weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text(f"${total_compras:.2f}")
    ], alignment=ft.MainAxisAlignment.CENTER))
    app.page.add(ft.Row([
        ft.Text("Balance:", weight=ft.FontWeight.BOLD, color="blue"),
        ft.Text(f"${balance:.2f}")
    ], alignment=ft.MainAxisAlignment.CENTER))

    app.page.add(ft.ElevatedButton("Generar CSV",
                                   on_click=lambda _: generar_csv_balance(app, total_ventas, total_compras,
                                                                          balance, desde, hasta,
                                                                          producto_nombre, cliente_nombre,
                                                                          proveedor_nombre)))
    app.page.add(ft.ElevatedButton("Volver", on_click=lambda _: app.main_menu()))
    app.page.update()

def generar_csv_balance(app: BaseApp, total_ventas, total_compras, balance, desde, hasta, producto_nombre, cliente_nombre,
                        proveedor_nombre):
    """
    Genera un archivo CSV con el reporte de balance.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        total_ventas (float): Total de ventas.
        total_compras (float): Total de compras.
        balance (float): Balance financiero.
        desde (str): Fecha de inicio del reporte.
        hasta (str): Fecha de fin del reporte.
        producto_nombre (Optional[str]): Nombre del producto filtrado.
        cliente_nombre (Optional[str]): Nombre del cliente filtrado.
        proveedor_nombre (Optional[str]): Nombre del proveedor filtrado.
    """
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

    ruta_archivo = app.generar_csv(nombre_archivo, encabezados, datos)
    if ruta_archivo:
        mensaje = f"Archivo CSV del balance generado: {ruta_archivo}"
    else:
        mensaje = "Error al generar el archivo CSV del balance"

    # Mostrar mensaje de éxito o error
    app.mostrar_mensaje(mensaje, "green")  # Añade el color aquí

