# reporte_productos.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_PRODUCTOS = "Reporte de Productos"

def listar_productos(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None):
    """
    Lista y muestra los productos en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
    """
    productos = _obtener_productos(app, desde, hasta)
    elementos = _crear_elementos_productos(productos)
    app._agregar_reporte(TITULO_PRODUCTOS, elementos, desde, hasta)

def _obtener_productos(app: BaseApp, desde: Optional[str], hasta: Optional[str]):
    """
    Obtiene la lista de productos desde la base de datos.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte.
        hasta (Optional[str]): Fecha de fin del reporte.

    Returns:
        List[Tuple]: Lista de tuplas con los datos de los productos.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT p.id, p.nombre, p.stock, p.precio AS precio_venta,
                   (SELECT c.precio_costo
                    FROM Compras c
                    WHERE c.producto_id = p.id
                    ORDER BY c.fecha DESC
                    LIMIT 1) AS precio_costo
            FROM Productos p
        """
        params = []
        where_clauses = []

        if desde and hasta:
            where_clauses.append("p.fecha BETWEEN ? AND ?")
            params.extend([desde, hasta])

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        cursor.execute(query, params)
        return cursor.fetchall()

def _crear_elementos_productos(productos):
    """
    Crea los elementos de la interfaz de usuario para mostrar los productos.

    Args:
        productos (List[Tuple]): Lista de tuplas con los datos de los productos.

    Returns:
        List[ft.Row]: Lista de filas con los datos de los productos.
    """
    return [
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

