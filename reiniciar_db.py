# reiniciar_db.py
import flet as ft
from database import create_connection, create_tables

class ReiniciarDBApp:
    def __init__(self, page, main_menu_callback):
        """
        Constructor de la clase ReiniciarDBApp.

        Args:
            page (ft.Page): La página principal de la aplicación.
            main_menu_callback (function): Función de devolución de llamada para volver al menú principal.
        """
        self.page = page
        self.main_menu_callback = main_menu_callback

    def reiniciar_base_de_datos(self):
        """
        Reinicia la base de datos eliminando todas las tablas existentes y volviéndolas a crear.
        """
        conn = create_connection()
        cursor = conn.cursor()

        # Eliminar todas las tablas
        cursor.execute("DROP TABLE IF EXISTS Ventas")
        cursor.execute("DROP TABLE IF EXISTS Compras")
        cursor.execute("DROP TABLE IF EXISTS Productos")
        cursor.execute("DROP TABLE IF EXISTS Clientes")
        cursor.execute("DROP TABLE IF EXISTS Proveedores")

        conn.commit()
        conn.close()

        # Volver a crear las tablas
        create_tables()

        self.mostrar_mensaje("Base de datos reiniciada con éxito", "green")
        self.main_menu()

    def main_menu(self):
        """
        Muestra el menú principal para reiniciar la base de datos.
        """
        def confirmar_reinicio(e):
            """
            Muestra un mensaje de confirmación antes de reiniciar la base de datos.

            Args:
                e: Evento de clic.
            """
            self.page.controls.clear()
            self.page.add(
                ft.Text("¿Estás seguro de que deseas reiniciar la base de datos?", size=24),
                ft.ElevatedButton("Sí, reiniciar", on_click=lambda _: self.reiniciar_base_de_datos()),
                ft.ElevatedButton("No, volver", on_click=lambda _: self.main_menu_callback())
            )
            self.page.update()

        self.page.controls.clear()
        self.page.add(
            ft.Text("Reiniciar Base de Datos", size=24),
            ft.ElevatedButton("Reiniciar Base de Datos", on_click=confirmar_reinicio),
            ft.ElevatedButton("Volver al Menú Principal", on_click=lambda _: self.main_menu_callback())
        )
        self.page.update()

    def mostrar_mensaje(self, mensaje, color):
        """
        Muestra un mensaje en la página.

        Args:
            mensaje (str): Mensaje a mostrar.
            color (str): Color del mensaje.
        """
        self.page.add(ft.Text(mensaje, color=color))
        self.page.update()

def reiniciar_db_app(page: ft.Page, main_menu_callback):
    """
    Función principal que inicializa la aplicación de reinicio de la base de datos.

    Args:
        page (ft.Page): La página principal de la aplicación.
        main_menu_callback (function): Función de devolución de llamada para volver al menú principal.
    """
    app = ReiniciarDBApp(page, main_menu_callback)
    app.main_menu()

