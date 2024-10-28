# nav_ruta_vci.py
import os

# Como compilar y generar un EXE con nuitka:
# nuitka --windows-console-mode=disable --standalone --onefile --enable-plugin=tk-inter --output-dir=dist --output-filename=Inc_Sis_Venta.exe nav_ruta_vci.py

# Función para navegar por la ruta 'VCI'
def navegar_ruta_vci():
    # Lista de unidades a verificar
    unidades = ['C', 'D', 'E']
    ruta_vci = None  # Aquí se almacenará la ruta válida encontrada

    # Buscar la ruta en las unidades disponibles
    for unidad in unidades:
        ruta = fr"{unidad}:\VCI"  # Crear la ruta para cada unidad
        if os.path.exists(ruta):
            print(f"Ruta encontrada: {ruta}")
            ruta_vci = ruta
            break

    # Si se encuentra la ruta, cambiamos al directorio
    if ruta_vci:
        try:
            os.chdir(ruta_vci)
            print(f"Directorio actual: {os.getcwd()}")

            # Ejecutar el archivo VentaCompraInv.exe
            os.system("VentaCompraInv.exe")

        except Exception as e:
            print(f"Error al intentar cambiar al directorio: {e}")

    else:
        print("La ruta 'VCI' no fue encontrada en las unidades C, D o E.")

# Ejecutar la función
navegar_ruta_vci()
