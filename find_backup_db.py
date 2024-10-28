# find_backup_db.py
import os
import shutil
import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
import queue

# Como crear el EXE con nuitka:
# nuitka --windows-console-mode=disable --enable-plugin=tk-inter --standalone --onefile --output-dir=dist find_backup_db.py

# Función para crear, buscar y restaurar la base de datos de backup
class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Respaldo de Base de Datos")
        self.root.geometry("400x250")

        self.label = tk.Label(root, text="Presione 'Iniciar Respaldo' para comenzar")
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.button_backup = tk.Button(root, text="Iniciar Respaldo", command=self.iniciar_respaldo)
        self.button_backup.pack(pady=10)

        self.button_restore = tk.Button(root, text="Restaurar Respaldo", command=self.iniciar_restaurar)
        self.button_restore.pack(pady=10)

        self.button_terminate = tk.Button(root, text="Terminar", command=self.terminar_aplicacion)
        self.button_terminate.pack(pady=10)

        self.stop_search = threading.Event()
        self.message_queue = queue.Queue()
        self.is_running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.after(100, self.check_messages)

    # Función para cerrar la aplicación
    def on_closing(self):
        self.is_running = False
        self.stop_search.set()
        self.root.destroy()

    # Función para comprobar los mensajes
    def check_messages(self):
        if not self.is_running:
            return
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message[0] == "showinfo":
                    messagebox.showinfo(message[1], message[2])
                elif message[0] == "showerror":
                    messagebox.showerror(message[1], message[2])
                elif message[0] == "showwarning":
                    messagebox.showwarning(message[1], message[2])
                elif message[0] == "update_label":
                    self.label.config(text=message[1])
                elif message[0] == "update_progress":
                    self.progress["value"] = message[1]
        except queue.Empty:
            pass
        finally:
            if self.is_running:
                self.root.after(100, self.check_messages)

    # Función para buscar la base de datos
    def buscar_base_de_datos(self, nombre_bd, ruta_inicial):
        try:
            for root, dirs, files in os.walk(ruta_inicial):
                if self.stop_search.is_set():
                    return None
                for file in files:
                    if self.stop_search.is_set():
                        return None
                    if file == nombre_bd:
                        return os.path.join(root, file)
                    self.message_queue.put(("update_progress", self.progress["value"] + 1))
            return None
        except Exception as e:
            self.message_queue.put(("showerror", "Error", f"Error al buscar la base de datos: {str(e)}"))
            return None

    # Función para respaldar la base de datos
    def respaldar_base_de_datos(self, ruta_bd, ruta_respaldo):
        try:
            nombre_bd = os.path.basename(ruta_bd)
            fecha_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_respaldo = f"{nombre_bd}_{fecha_hora}.bak"
            ruta_respaldo_completa = os.path.join(ruta_respaldo, nombre_respaldo)

            shutil.copy2(ruta_bd, ruta_respaldo_completa)

            # Guardar la ruta original en un archivo de registro
            with open(os.path.join(ruta_respaldo, "backup_log.txt"), "a") as log_file:
                log_file.write(f"{nombre_respaldo},{ruta_bd}\n")

            return ruta_respaldo_completa
        except Exception as e:
            self.message_queue.put(("showerror", "Error", f"Error al respaldar la base de datos: {str(e)}"))
            return None

    # Función para restaurar la base de datos
    def restaurar_base_de_datos(self, ruta_respaldo):
        try:
            backups = [f for f in os.listdir(ruta_respaldo) if f.startswith("inventario.db_") and f.endswith(".bak")]
            if not backups:
                self.message_queue.put(("showwarning", "No hay respaldos disponibles", "No se encontraron respaldos para restaurar."))
                return None

            backups.sort(reverse=True)
            nombre_respaldo = backups[0]
            ruta_respaldo_completa = os.path.join(ruta_respaldo, nombre_respaldo)

            # Recuperar la ruta original desde el archivo de registro
            with open(os.path.join(ruta_respaldo, "backup_log.txt"), "r") as log_file:
                for line in log_file:
                    if nombre_respaldo in line:
                        ruta_bd = line.split(",")[1].strip()
                        shutil.copy2(ruta_respaldo_completa, ruta_bd)
                        return ruta_bd

            self.message_queue.put(("showwarning", "Ruta original no encontrada", "No se pudo encontrar la ruta original en el archivo de registro."))
            return None
        except Exception as e:
            self.message_queue.put(("showerror", "Error", f"Error al restaurar la base de datos: {str(e)}"))
            return None

    # Función para iniciar el proceso de respaldo
    def iniciar_respaldo(self):
        self.button_backup.config(state=tk.DISABLED)
        self.button_restore.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.root.update_idletasks()
        self.message_queue.put(("update_label", "Iniciando búsqueda..."))
        self.stop_search.clear()

        nombre_bd = "inventario.db"
        ruta_inicial = "C:\\"
        ruta_respaldo = "C:\\VCI\\respaldos_db"

        # Función para realizar la tarea de respaldo
        def tarea_respaldo():
            ruta_bd = self.buscar_base_de_datos(nombre_bd, ruta_inicial)
            if ruta_bd and not self.stop_search.is_set():
                self.message_queue.put(
                    ("showinfo", "Ubicación de la Base de Datos", f"Base de datos encontrada en: {ruta_bd}"))

                if not os.path.exists(ruta_respaldo):
                    try:
                        os.makedirs(ruta_respaldo)
                    except Exception as e:
                        self.message_queue.put(
                            ("showerror", "Error", f"Error al crear la carpeta de respaldo: {str(e)}"))
                        return

                ruta_respaldo_completa = self.respaldar_base_de_datos(ruta_bd, ruta_respaldo)
                if ruta_respaldo_completa:
                    self.progress["value"] = 100
                    self.root.update_idletasks()
                    self.message_queue.put(
                        ("showinfo", "Respaldo Completado", f"Respaldo creado en: {ruta_respaldo_completa}"))
            elif not self.stop_search.is_set():
                self.message_queue.put(("showwarning", "Base de Datos No Encontrada",
                                        f"No se encontró la base de datos {nombre_bd} en la ruta {ruta_inicial}"))

            if self.is_running:
                self.root.after(100, self.finalizar_busqueda)

        threading.Thread(target=tarea_respaldo, daemon=True).start()

    # Función para iniciar el proceso de restauración
    def iniciar_restaurar(self):
        self.button_backup.config(state=tk.DISABLED)
        self.button_restore.config(state=tk.DISABLED)
        self.progress["value"] = 0
        self.root.update_idletasks()
        self.message_queue.put(("update_label", "Iniciando restauración..."))
        self.stop_search.clear()

        ruta_respaldo = "C:\\VCI\\respaldos_db"

        # Función para realizar la tarea de restauración
        def tarea_restaurar():
            ruta_restaurada = self.restaurar_base_de_datos(ruta_respaldo)
            if ruta_restaurada:
                self.progress["value"] = 100
                self.root.update_idletasks()
                self.message_queue.put(
                    ("showinfo", "Restauración Completada", f"Base de datos restaurada en: {ruta_restaurada}"))
            else:
                self.message_queue.put(("showwarning", "Restauración Fallida", "No se pudo restaurar la base de datos."))

            if self.is_running:
                self.root.after(100, self.finalizar_busqueda)

        threading.Thread(target=tarea_restaurar, daemon=True).start()

    # Función para finalizar la busqueda
    def finalizar_busqueda(self):
        self.stop_search.set()
        self.progress["value"] = 100
        self.root.update_idletasks()
        self.button_backup.config(state=tk.NORMAL)
        self.button_restore.config(state=tk.NORMAL)
        self.message_queue.put(("update_label", "Búsqueda finalizada"))
        self.button_backup.destroy()  # Eliminar el botón "Iniciar Respaldo"
        self.button_restore.destroy()  # Eliminar el botón "Iniciar Restauración"

    # Función para terminar la aplicación
    def terminar_aplicacion(self):
        self.is_running = False
        self.stop_search.set()
        self.root.destroy()

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()
