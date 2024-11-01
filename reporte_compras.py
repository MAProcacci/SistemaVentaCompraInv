# reporte_compras.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_COMPRAS = "Reporte de Compras"

def listar_compras(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None,
                   producto_id: Optional[int] = None, proveedor_id: Optional[int] = None):
    """
    Lista y muestra las compras en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
        producto_id (Optional[int]): ID del producto a filtrar. Por defecto es None.
        proveedor_id (Optional[int]): ID del proveedor a filtrar. Por defecto es None.
    """
    query, params = _construir_query_compras(desde, hasta, producto_id, proveedor_id)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        compras = cursor.fetchall()

    elementos = _crear_elementos_compras(compras)
    app._agregar_reporte(TITULO_COMPRAS, elementos, desde, hasta)

def _construir_query_compras(desde: Optional[str], hasta: Optional[str], producto_id: Optional[int],
                             proveedor_id: Optional[int]):
    """
    Construye la consulta SQL para obtener las compras.

    Args:
        desde (Optional[str]): Fecha de inicio del reporte.
        hasta (Optional[str]): Fecha de fin del reporte.
        producto_id (Optional[int]): ID del producto a filtrar.
        proveedor_id (Optional[int]): ID del proveedor a filtrar.

    Returns:
        Tuple[str, List]: Consulta SQL y lista de parámetros.
    """
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

def _crear_elementos_compras(compras):
    """
    Crea los elementos de la interfaz de usuario para mostrar las compras.

    Args:
        compras (List[Tuple]): Lista de tuplas con los datos de las compras.

    Returns:
        List[ft.Row]: Lista de filas con los datos de las compras.
    """
    return [
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

