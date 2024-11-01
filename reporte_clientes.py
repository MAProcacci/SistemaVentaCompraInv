# reporte_clientes.py
import flet as ft
from typing import Optional
from libreria import BaseApp, get_db_connection

TITULO_CLIENTES = "Reporte de Clientes"

def listar_clientes(app: BaseApp, desde: Optional[str] = None, hasta: Optional[str] = None):
    """
    Lista y muestra los clientes en un reporte.

    Args:
        app (BaseApp): Instancia de la aplicación base.
        desde (Optional[str]): Fecha de inicio del reporte. Por defecto es None.
        hasta (Optional[str]): Fecha de fin del reporte. Por defecto es None.
    """
    clientes = _obtener_clientes(app)
    elementos = _crear_elementos_clientes(clientes)
    app._agregar_reporte(TITULO_CLIENTES, elementos, desde, hasta)

def _obtener_clientes(app: BaseApp):
    """
    Obtiene la lista de clientes desde la base de datos.

    Args:
        app (BaseApp): Instancia de la aplicación base.

    Returns:
        List[Tuple]: Lista de tuplas con los datos de los clientes.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clientes")
        return cursor.fetchall()

def _crear_elementos_clientes(clientes):
    """
    Crea los elementos de la interfaz de usuario para mostrar los clientes.

    Args:
        clientes (List[Tuple]): Lista de tuplas con los datos de los clientes.

    Returns:
        List[ft.Row]: Lista de filas con los datos de los clientes.
    """
    return [
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

