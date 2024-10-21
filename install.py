# install.py
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import winshell
import win32com.client

# Como crear el EXE con nuitka:
# nuitka --windows-console-mode=disable --enable-plugin=tk-inter --standalone --onefile --output-dir=dist install.py

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instalador de VentaCompraInven")
        self.root.geometry("400x200")

        self.label = tk.Label(root, text="Seleccione la unidad de instalación:")
        self.label.pack(pady=10)

        self.drive_var = tk.StringVar(value="C:")
        self.drive_menu = ttk.Combobox(root, textvariable=self.drive_var, values=self.get_available_drives())
        self.drive_menu.pack(pady=10)

        self.install_button = tk.Button(root, text="Instalar", command=self.install)
        self.install_button.pack(pady=20)

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def get_available_drives(self):
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        return drives

    def install(self):
        selected_drive = self.drive_var.get()
        install_path = os.path.join(selected_drive, "VCI")
        sumatra_installer_path = os.path.join(install_path, "SumatraPDF_Installer")

        try:
            # Crear el directorio VCI
            os.makedirs(install_path, exist_ok=True)

            # Copiar VentaCompraInv.exe
            self.progress["value"] = 20
            self.root.update_idletasks()
            shutil.copy("VentaCompraInv.exe", install_path)

            # Crear el directorio SumatraPDF_Installer
            os.makedirs(sumatra_installer_path, exist_ok=True)

            # Copiar SumatraPDF-3.5.2-64-install.exe
            self.progress["value"] = 60
            self.root.update_idletasks()
            shutil.copy("SumatraPDF-3.5.2-64-install.exe", sumatra_installer_path)

            # Crear acceso directo en el escritorio
            self.create_shortcut(os.path.join(install_path, "VentaCompraInv.exe"))

            self.progress["value"] = 100
            self.root.update_idletasks()

            messagebox.showinfo("Instalación Completa", "La instalación se ha completado con éxito.")
            self.root.destroy()  # Cerrar la ventana principal y finalizar el programa

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante la instalación: {str(e)}")

    def create_shortcut(self, target_path):
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Sistema VentaCompraInv.lnk")
        icon_path = "ruta_del_icono.ico"  # Reemplaza con la ruta del icono que deseas usar

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = icon_path
        shortcut.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
