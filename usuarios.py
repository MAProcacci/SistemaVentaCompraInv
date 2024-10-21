# usuarios.py
from cryptography.fernet import Fernet

def cargar_credenciales():
    """
    Carga las credenciales de usuario desde un archivo encriptado.

    Returns:
        tuple: Una tupla que contiene la clave de encriptación y una lista de usuarios desencriptados.
    """
    with open("password.txt", "rb") as file:
        key = file.readline().strip()
        usuarios_encriptados = file.readlines()
    cipher_suite = Fernet(key)
    usuarios = []
    for usuario_encriptado in usuarios_encriptados:
        usuario_encriptado = usuario_encriptado.strip()
        try:
            usuario = cipher_suite.decrypt(usuario_encriptado).decode()
            usuarios.append(usuario)
        except Exception as e:
            print(f"Error al desencriptar usuario: {e}")
    return key, usuarios

def guardar_credenciales(key, usuarios):
    """
    Guarda las credenciales de usuario en un archivo encriptado.

    Args:
        key (bytes): La clave de encriptación.
        usuarios (list): Lista de usuarios a guardar.
    """
    with open("password.txt", "wb") as file:
        file.write(key + b"\n")
        cipher_suite = Fernet(key)
        for usuario in usuarios:
            usuario_encriptado = cipher_suite.encrypt(usuario.encode())
            file.write(usuario_encriptado + b"\n")

def crear_usuario(nuevo_usuario, nueva_password, key):
    """
    Crea un nuevo usuario y lo guarda en el archivo de credenciales encriptado.

    Args:
        nuevo_usuario (str): Nombre del nuevo usuario.
        nueva_password (str): Contraseña del nuevo usuario.
        key (bytes): La clave de encriptación.
    """
    cipher_suite = Fernet(key)
    usuario_encriptado = cipher_suite.encrypt(f"{nuevo_usuario}:{nueva_password}".encode())
    with open("password.txt", "ab") as file:
        file.write(usuario_encriptado + b"\n")

def modificar_usuario(usuario_seleccionado, nueva_password, key):
    """
    Modifica la contraseña de un usuario existente en el archivo de credenciales encriptado.

    Args:
        usuario_seleccionado (str): Nombre del usuario a modificar.
        nueva_password (str): Nueva contraseña del usuario.
        key (bytes): La clave de encriptación.
    """
    _, usuarios = cargar_credenciales()
    usuarios_actualizados = []
    for usuario in usuarios:
        usuario_name, _ = usuario.split(":")
        if usuario_name == usuario_seleccionado:
            usuarios_actualizados.append(f"{usuario_name}:{nueva_password}")
        else:
            usuarios_actualizados.append(usuario)
    guardar_credenciales(key, usuarios_actualizados)

def eliminar_usuario(usuario_seleccionado, key):
    """
    Elimina un usuario del archivo de credenciales encriptado.

    Args:
        usuario_seleccionado (str): Nombre del usuario a eliminar.
        key (bytes): La clave de encriptación.
    """
    _, usuarios = cargar_credenciales()
    usuarios_actualizados = [usuario for usuario in usuarios if usuario.split(":")[0] != usuario_seleccionado]
    guardar_credenciales(key, usuarios_actualizados)
