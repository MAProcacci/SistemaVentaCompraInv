# reporte_ventas.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_VENTAS = "Reporte de Ventas"

def listar_ventas(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None, producto_id: Optional[int] = None,
                  cliente_id: Optional[int] = None):
    """
    Lista y muestra las ventas en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        producto_id (Optional[int]): ID del producto a filtrar. Por defecto es None.
        cliente_id (Optional[int]): ID del cliente a filtrar. Por defecto es None.
    """
    query, params = _construir_query_ventas(desde, hasta, producto_id, cliente_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        ventas = cursor.fetchall()

    elementos = _crear_elementos_ventas(ventas)
    app._agregar_reporte(TITULO_VENTAS, elementos, desde, hasta)

def _construir_query_ventas(desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                            cliente_id: Optional[int]):
    """
    Construye la consulta SQL para obtener las ventas.

    Args:
        desde (Optional[str]): Fecha de inicio del reporte.
        hasta (Optional[str]): Fecha de fin del reporte.
        producto_id (Optional[int]): ID del producto a filtrar.
        cliente_id (Optional[int]): ID del cliente a filtrar.

    Returns:
        Tuple[str, List]: Consulta SQL y lista de parámetros.
    """
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

def _crear_elementos_ventas(ventas):
    """
    Crea los elementos de la interfaz de usuario para mostrar las ventas.

    Args:
        ventas (List[Tuple]): Lista de tuplas con los datos de las ventas.

    Returns:
        List[ft.Row]: Lista de filas con los datos de las ventas.
    """
    return [
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

