# reporte_devoluciones.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_DEVOLUCIONES = "Reporte de Devoluciones"

def listar_devoluciones(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None,
                        producto_id: Optional[int] = None, cliente_id: Optional[int] = None):
    """
    Lista y muestra las devoluciones en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        producto_id (Optional[int]): ID del producto a filtrar. Por defecto es None.
        cliente_id (Optional[int]): ID del cliente a filtrar. Por defecto es None.
    """
    query, params = _construir_query_devoluciones(desde, hasta, producto_id, cliente_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        devoluciones = cursor.fetchall()

    elementos = _crear_elementos_devoluciones(devoluciones)
    app._agregar_reporte(TITULO_DEVOLUCIONES, elementos, desde, hasta)

def _construir_query_devoluciones(desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                                  cliente_id: Optional[int]):
    """
    Construye la consulta SQL para obtener las devoluciones.

    Args:
        desde (Optional[str]): Fecha de inicio del reporte.
        hasta (Optional[str]): Fecha de fin del reporte.
        producto_id (Optional[int]): ID del producto a filtrar.
        cliente_id (Optional[int]): ID del cliente a filtrar.

    Returns:
        Tuple[str, List]: Consulta SQL y lista de parámetros.
    """
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

def _crear_elementos_devoluciones(devoluciones):
    """
    Crea los elementos de la interfaz de usuario para mostrar las devoluciones.

    Args:
        devoluciones (List[Tuple]): Lista de tuplas con los datos de las devoluciones.

    Returns:
        List[ft.Row]: Lista de filas con los datos de las devoluciones.
    """
    return [
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

