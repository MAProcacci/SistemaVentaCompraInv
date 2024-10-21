# password.py

from cryptography.fernet import Fernet
import os

def password_app():
    # Verificar si el archivo 'password.txt' ya existe
    if not os.path.exists("password.txt"):
        # Generar una clave de encriptación
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        # Mostrar la clave generada (para copiarla en tu código)
        # print(key)

        # Credenciales
        usuarios = [
            "admin:admin",
            "user1:password1",
            "user2:password2"
        ]

        # Guardar la clave y las credenciales encriptadas en un archivo
        with open("password.txt", "wb") as file:
            file.write(key + b"\n")
            for usuario in usuarios:
                usuario_encriptado = cipher_suite.encrypt(usuario.encode())
                file.write(usuario_encriptado + b"\n")
    #else:
        #print("El archivo 'password.txt' ya existe. No se creará nuevamente.")

# Si deseas ejecutar la función directamente desde este archivo
if __name__ == "__main__":
    password_app()
