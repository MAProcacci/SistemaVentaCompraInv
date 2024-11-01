# reporte_proveedores.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_PROVEEDORES = "Reporte de Proveedores"

def listar_proveedores(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None):
    """
    Lista y muestra los proveedores en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
    """
    proveedores = _obtener_proveedores(app)
    elementos = _crear_elementos_proveedores(proveedores)
    app._agregar_reporte(TITULO_PROVEEDORES, elementos, desde, hasta)

def _obtener_proveedores(app: BaseApp):
    """
    Obtiene la lista de proveedores desde la base de datos.

    Args:
        app (BaseApp): Instancia de la aplicación base.

    Returns:
        List[Tuple]: Lista de tuplas con los datos de los proveedores.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Proveedores")
        return cursor.fetchall()

def _crear_elementos_proveedores(proveedores):
    """
    Crea los elementos de la interfaz de usuario para mostrar los proveedores.

    Args:
        proveedores (List[Tuple]): Lista de tuplas con los datos de los proveedores.

    Returns:
        List[ft.Row]: Lista de filas con los datos de los proveedores.
    """
    return [
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

