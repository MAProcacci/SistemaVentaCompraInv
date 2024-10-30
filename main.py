# main.py
import flet as ft
from typing import List, Tuple, Callable
import password
from producto import producto_app
from cliente import cliente_app
from proveedor import proveedor_app
from ventas import ventas_app
from compras import compras_app
from reportes import reportes_app
from reiniciar_db import reiniciar_db_app
from usuarios import cargar_credenciales, crear_usuario, modificar_usuario, eliminar_usuario
from devoluciones import devoluciones_app
from graficos import graficos_app
import database
import os
import subprocess
from datetime import datetime

# Website de donde instalar SumatraPDF: https://www.sumatrapdfreader.org/download-free-pdf-viewer
# Se usa en los modulos de 'reportes.py y 'nav_reportes_pdf.py' para imprimir y visulizar los reportes en PDF.

# Como compilar y generar un EXE con nuitka: nuitka --windows-console-mode=disable --standalone --onefile --output-dir=dist main.py
# Y de esta manera le cambiamos el nombre del ejecutable a VentaCompraInv.exe:
# nuitka --windows-console-mode=disable --standalone --onefile --enable-plugin=tk-inter --output-dir=dist --output-filename=VentaCompraInv.exe main.py

# Constantes
TITULO_APP = "Inversiones Torino C.A. - Sistema de Ventas e Inventario"
TAMANO_TITULO = 24
COLOR_ERROR = "red"
COLOR_EXITO = "black"
COLOR_SNACKBAR = "white"

class MainApp:
    def __init__(self, page: ft.Page):
        """
        Constructor de la clase MainApp.
        Inicializa la página y configura el título y la alineación.

        Args:
            page (ft.Page): La página principal de la aplicación.
        """
        self.page = page
        self.page.title = TITULO_APP
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        self.current_user: str = None
        self.key: str = None
        self.usuarios_reales: List[str] = []

    def validar_credenciales(self, usuario_ingresado: str, password_ingresado: str) -> bool:
        """
        Valida las credenciales de usuario.

        Args:
            usuario_ingresado (str): Nombre de usuario ingresado.
            password_ingresado (str): Contraseña ingresada.

        Returns:
            bool: True si las credenciales son válidas, False en caso contrario.
        """
        for usuario_real in self.usuarios_reales:
            try:
                usuario_real, password_real = usuario_real.split(":")
                if usuario_ingresado == usuario_real and password_ingresado == password_real:
                    self.current_user = usuario_real
                    return True
            except ValueError as e:
                print(f"Error al validar credenciales: {e}")
        return False

    def login_screen(self) -> None:
        """Muestra la pantalla de inicio de sesión."""
        self.page.controls.clear()
        self.key, self.usuarios_reales = cargar_credenciales()

        def validar_login(e):
            usuario_ingresado = usuario_field.value
            password_ingresado = password_field.value

            if self.validar_credenciales(usuario_ingresado, password_ingresado):
                self.main_menu()
            else:
                #error_message.visible = True
                self.mostrar_mensaje("Acceso denegado - Usuario y/o Password no autorizado", COLOR_ERROR)
                self.page.update()

        usuario_field = ft.TextField(label="Usuario", border_color=ft.colors.OUTLINE)
        password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, border_color=ft.colors.OUTLINE)
        error_message = ft.Text("Acceso denegado - Usuario y/o Password no autorizado", color=COLOR_ERROR, visible=False)

        self.page.add(
            ft.Text("Iniciar Sesión", size=TAMANO_TITULO, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=20, color="transparent"),
            ft.Column(
                [
                    usuario_field,
                    password_field,
                    ft.ElevatedButton("Ingresar", on_click=validar_login),
                    error_message,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=300,
            )
        )
        self.page.update()

    def main_menu(self) -> None:
        """Muestra el menú principal de la aplicación."""
        self.page.controls.clear()
        self.page.add(
            ft.Text("Menú Principal", size=TAMANO_TITULO, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Divider(height=20, color="transparent"),
            ft.Column([
                self._create_menu_row("Productos", ft.icons.SHOPPING_BAG, self.open_productos,
                                      "Clientes", ft.icons.PERSON, self.open_clientes),
                self._create_menu_row("Proveedores", ft.icons.BUILD, self.open_proveedores,
                                      "Ventas", ft.icons.ATTACH_MONEY, self.open_ventas),
                self._create_menu_row("Compras", ft.icons.SHOPPING_CART, self.open_compras,
                                      "Reportes", ft.icons.DESCRIPTION, self.open_reportes),
                self._create_menu_row("Devoluciones", ft.icons.ARROW_BACK, self.open_devoluciones,
                                      "Gráficos", ft.icons.BAR_CHART, self.open_graficos),
                ft.Row([
                    ft.ElevatedButton("Mantenimiento", icon=ft.icons.SETTINGS, on_click=self.open_mantenimiento),
                    ft.Divider(height=20, color="transparent"),
                    ft.ElevatedButton("Cambio de Usuario", icon=ft.icons.SWAP_HORIZ, on_click=self.cambiar_usuario),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.ElevatedButton("Salir", on_click=lambda _: self.page.window.close())],
                       alignment=ft.MainAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
        self.page.update()

    def _create_menu_row(self, text1: str, icon1: str, on_click1: Callable,
                         text2: str, icon2: str, on_click2: Callable) -> ft.Row:
        """Crea una fila de botones para el menú principal."""
        return ft.Row([
            ft.ElevatedButton(text1, icon=icon1, on_click=on_click1),
            ft.Divider(height=20, color="transparent"),
            ft.ElevatedButton(text2, icon=icon2, on_click=on_click2),
        ], alignment=ft.MainAxisAlignment.CENTER)

    def _open_app(self, app_function: Callable) -> None:
        """Abre una aplicación específica."""
        self.page.controls.clear()
        app_function(self.page, self.main_menu)
        self.page.update()

    def open_productos(self, _) -> None:
        """Abre la aplicación de gestión de productos."""
        self._open_app(producto_app)

    def open_clientes(self, _) -> None:
        """Abre la aplicación de gestión de clientes."""
        self._open_app(cliente_app)

    def open_proveedores(self, _) -> None:
        """Abre la aplicación de gestión de proveedores."""
        self._open_app(proveedor_app)

    def open_ventas(self, _) -> None:
        """Abre la aplicación de gestión de ventas."""
        self._open_app(ventas_app)

    def open_compras(self, _) -> None:
        """Abre la aplicación de gestión de compras."""
        self._open_app(compras_app)

    def open_reportes(self, _) -> None:
        """Abre la aplicación de reportes."""
        self._open_app(reportes_app)

    def open_devoluciones(self, _) -> None:
        """Abre la aplicación de gestión de devoluciones."""
        self._open_app(devoluciones_app)

    def open_graficos(self, _) -> None:
        """Abre la aplicación de gráficos."""
        self._open_app(graficos_app)

    def open_mantenimiento(self, _) -> None:
        """Abre la aplicación de mantenimiento."""
        self.page.controls.clear()
        self.mantenimiento_menu()
        self.page.update()

    def mantenimiento_menu(self) -> None:
        """Muestra el menú de mantenimiento."""
        self.page.controls.clear()
        if self.current_user == "admin":
            self.page.add(
                ft.Text("Mantenimiento", size=TAMANO_TITULO, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=20, color="transparent"),
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton("Reiniciar Base de Datos", icon=ft.icons.SETTINGS,
                                          on_click=self.reiniciar_db),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Crear Usuario", icon=ft.icons.PERSON_ADD, on_click=self.crear_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Modificar Usuario", icon=ft.icons.EDIT, on_click=self.modificar_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Eliminar Usuario", icon=ft.icons.DELETE, on_click=self.eliminar_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Abrir Instalador SumatraPDF", icon=ft.icons.DOWNLOAD,
                                          on_click=lambda _: abrir_instalador_sumatra_pdf(self)),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=20, color="transparent"),
                    ft.Row([
                        ft.ElevatedButton("Volver al Menú Principal", icon=ft.icons.ARROW_BACK,
                                          on_click=lambda _: self.main_menu()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.CENTER)
            )
        else:
            self.mostrar_mensaje("Acceso denegado - Solo el administrador puede acceder a esta sección", COLOR_ERROR)
            self.page.add(
                ft.Text("Acceso denegado - Solo el administrador puede acceder a esta sección", color=COLOR_ERROR),
                ft.Divider(height=20, color="transparent"),
                ft.Row([
                    ft.ElevatedButton("Volver al Menú Principal", icon=ft.icons.ARROW_BACK,
                                      on_click=lambda _: self.main_menu()),
                ], alignment=ft.MainAxisAlignment.CENTER),
            )
        self.page.update()

    def reiniciar_db(self, _) -> None:
        """Reinicia la base de datos."""
        reiniciar_db_app(self.page, self.main_menu)
        self.page.update()

    def crear_usuario(self, _) -> None:
        """Muestra la pantalla para crear un nuevo usuario."""
        self.page.controls.clear()

        def guardar_usuario(_):
            nuevo_usuario = nuevo_usuario_field.value
            nueva_password = nueva_password_field.value

            if nuevo_usuario and nueva_password:
                crear_usuario(nuevo_usuario, nueva_password, self.key)
                self.mostrar_mensaje("Usuario creado exitosamente", COLOR_EXITO)
                self.page.controls.clear()
                self.mantenimiento_menu()
            else:
                self.mostrar_mensaje("Por favor, ingrese un usuario y una contraseña", COLOR_ERROR)

        nuevo_usuario_field = ft.TextField(label="Nuevo Usuario")
        nueva_password_field = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True)

        self.page.add(
            ft.Column(
                [
                    nuevo_usuario_field,
                    nueva_password_field,
                    ft.Row([
                        ft.ElevatedButton("Guardar Usuario", on_click=guardar_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Cancelar", on_click=lambda _: self.mantenimiento_menu()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def modificar_usuario(self, _) -> None:
        """Muestra la pantalla para modificar un usuario existente."""
        self.page.controls.clear()

        def actualizar_usuario(_):
            usuario_seleccionado = usuario_dropdown.value
            nueva_password = nueva_password_field.value

            if usuario_seleccionado and nueva_password:
                modificar_usuario(usuario_seleccionado, nueva_password, self.key)
                self.mostrar_mensaje("Usuario modificado exitosamente", COLOR_EXITO)
                self.page.controls.clear()
                self.mantenimiento_menu()
            else:
                self.mostrar_mensaje("Por favor, seleccione un usuario y ingrese una nueva contraseña", COLOR_ERROR)

        _, usuarios_reales = cargar_credenciales()
        usuarios = [usuario.split(":")[0] for usuario in usuarios_reales]
        usuario_dropdown = ft.Dropdown(
            label="Seleccionar Usuario",
            options=[ft.dropdown.Option(usuario) for usuario in usuarios]
        )
        nueva_password_field = ft.TextField(label="Nueva Contraseña", password=True, can_reveal_password=True)

        self.page.add(
            ft.Column(
                [
                    usuario_dropdown,
                    nueva_password_field,
                    ft.Row([
                        ft.ElevatedButton("Actualizar Usuario", on_click=actualizar_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Cancelar", on_click=lambda _: self.mantenimiento_menu()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def eliminar_usuario(self, _) -> None:
        """Muestra la pantalla para eliminar un usuario existente."""
        self.page.controls.clear()

        def borrar_usuario(_):
            usuario_seleccionado = usuario_dropdown.value

            if usuario_seleccionado == "admin":
                self.mostrar_mensaje("No se puede eliminar el usuario 'admin'", COLOR_ERROR)
                return

            if usuario_seleccionado:
                eliminar_usuario(usuario_seleccionado, self.key)
                self.mostrar_mensaje("Usuario eliminado exitosamente", COLOR_EXITO)
                self.page.controls.clear()
                self.mantenimiento_menu()
            else:
                self.mostrar_mensaje("Por favor, seleccione un usuario para eliminar", COLOR_ERROR)

        _, usuarios_reales = cargar_credenciales()
        usuarios = [usuario.split(":")[0] for usuario in usuarios_reales]
        usuario_dropdown = ft.Dropdown(
            label="Seleccionar Usuario",
            options=[ft.dropdown.Option(usuario) for usuario in usuarios]
        )

        self.page.add(
            ft.Column(
                [
                    usuario_dropdown,
                    ft.Row([
                        ft.ElevatedButton("Eliminar  Usuario", on_click=borrar_usuario),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Cancelar", on_click=lambda _: self.mantenimiento_menu()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self.page.update()

    def cambiar_usuario(self, _) -> None:
        """Muestra la pantalla para cambiar el usuario actual."""
        self.page.controls.clear()

        def validar_cambio(_):
            usuario_ingresado = usuario_field.value
            password_ingresado = password_field.value

            if self.validar_credenciales(usuario_ingresado, password_ingresado):
                self.mostrar_mensaje("Usuario cambiado exitosamente", COLOR_EXITO)
                self.main_menu()
            else:
                self.mostrar_mensaje("Acceso denegado - Usuario y/o Password no autorizado", COLOR_ERROR)

        usuario_field = ft.TextField(label="Usuario")
        password_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True)

        self.page.add(
            ft.Text("Cambio de Usuario", size=TAMANO_TITULO, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=20, color="transparent"),
            ft.Column(
                [
                    usuario_field,
                    password_field,
                    ft.Row([
                        ft.ElevatedButton("Cambiar Usuario", on_click=validar_cambio),
                        ft.Divider(height=20, color="transparent"),
                        ft.ElevatedButton("Cancelar", on_click=lambda _: self.main_menu()),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                width=300,
            )
        )
        self.page.update()

    def reiniciar_numero_factura(self) -> None:
        """Reinicia el número de factura a '00000001'."""
        with database.create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Ventas SET factura_id = '00000001' WHERE id = (SELECT MAX(id) FROM Ventas)")
            conn.commit()
        self.mostrar_mensaje("Número de factura reiniciado a '00000001'", COLOR_ERROR)

    def mostrar_mensaje(self, mensaje: str, color: str) -> None:
        """
        Muestra un mensaje en un SnackBar.

        Args:
            mensaje (str): Mensaje a mostrar.
            color (str): Color del mensaje.
        """
        snack_bar = ft.SnackBar(ft.Text(mensaje, color=color, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SNACKBAR)
        self.page.overlay.append(snack_bar)  # Usar overlay en lugar de snack_bar
        snack_bar.open = True
        self.page.update()

        # Guardar el mensaje de error si el color es COLOR_ERROR
        if color == COLOR_ERROR:
            self.guardar_error(mensaje)

    def guardar_error(self, mensaje_error: str):
        ruta_errores = os.path.join(os.getcwd(), 'errores')
        os.makedirs(ruta_errores, exist_ok=True)

        fecha_hora = datetime.now().strftime("%m%d%y_%H%M")
        nombre_archivo = f"Error_{fecha_hora}.txt"
        ruta_archivo = os.path.join(ruta_errores, nombre_archivo)

        with open(ruta_archivo, 'w') as archivo:
            archivo.write(mensaje_error)

def abrir_instalador_sumatra_pdf(main_app_instance):
    # Ruta al instalador de SumatraPDF
    ruta_instalador = os.path.join(os.getcwd(), 'SumatraPDF_Installer\\SumatraPDF-3.5.2-64-install.exe')

    # Verificar si el archivo existe
    if not os.path.exists(ruta_instalador):
        mensaje_error = f"El archivo de instalación de SumatraPDF no se encuentra en la ruta: {ruta_instalador}"
        main_app_instance.mostrar_mensaje(mensaje_error, COLOR_ERROR)
        main_app_instance.guardar_error(mensaje_error)
        return

    try:
        # Abrir el instalador
        subprocess.Popen([ruta_instalador], shell=True)
        main_app_instance.mostrar_mensaje("El instalador de SumatraPDF se ha abierto correctamente.", COLOR_EXITO)
    except Exception as e:
        mensaje_error = f"Error al abrir el instalador de SumatraPDF: {str(e)}"
        main_app_instance.mostrar_mensaje(mensaje_error, COLOR_ERROR)
        main_app_instance.guardar_error(mensaje_error)

def main(page: ft.Page) -> None:
    """
    Función principal que inicializa la aplicación y muestra la pantalla de inicio de sesión.

    Args:
        page (ft.Page): La página principal de la aplicación.
    """
    app = MainApp(page)
    password.password_app()
    app.login_screen()

if __name__ == "__main__":
    database.create_tables()
    ft.app(target=main)

