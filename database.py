# database.py
import sqlite3

def create_connection():
    """
    Crea y retorna una conexión a la base de datos SQLite.

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    conn = sqlite3.connect('inventario.db')
    return conn

def create_tables():
    """
    Crea las tablas necesarias en la base de datos si no existen.

    Las tablas creadas son:
    - Productos: Almacena información sobre los productos.
    - Clientes: Almacena información sobre los clientes.
    - Proveedores: Almacena información sobre los proveedores.
    - Ventas: Almacena información sobre las ventas realizadas.
    - Compras: Almacena información sobre las compras realizadas.
    - Devoluciones: Almacena información sobre las devoluciones realizadas.
    """
    conn = create_connection()
    cursor = conn.cursor()

    # Tabla de Productos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único del producto
        nombre TEXT NOT NULL,  -- Nombre del producto
        descripcion TEXT,  -- Descripción del producto
        precio REAL NOT NULL,  -- Precio del producto
        stock INTEGER NOT NULL  -- Cantidad en stock del producto
    )
    ''')

    # Tabla de Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único del cliente
        nombre TEXT NOT NULL,  -- Nombre del cliente
        telefono TEXT,  -- Número de teléfono del cliente
        email TEXT  -- Dirección de correo electrónico del cliente
    )
    ''')

    # Tabla de Proveedores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único del proveedor
        nombre TEXT NOT NULL,  -- Nombre del proveedor
        telefono TEXT,  -- Número de teléfono del proveedor
        email TEXT  -- Dirección de correo electrónico del proveedor
    )
    ''')

    # Tabla de Ventas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único de la venta
        cliente_id INTEGER,  -- Identificador del cliente que realizó la compra
        producto_id INTEGER,  -- Identificador del producto vendido
        cantidad INTEGER NOT NULL,  -- Cantidad de productos vendidos
        fecha DATE NOT NULL,  -- Fecha de la venta
        factura_id TEXT NOT NULL,  -- Número de factura de la venta
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id),  -- Clave foránea que referencia al cliente
        FOREIGN KEY (producto_id) REFERENCES Productos(id)  -- Clave foránea que referencia al producto
    )
    ''')

    # Tabla de Compras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único de la compra
        proveedor_id INTEGER,  -- Identificador del proveedor que suministró los productos
        producto_id INTEGER,  -- Identificador del producto comprado
        cantidad INTEGER,  -- Cantidad de productos comprados
        fecha TEXT,  -- Fecha de la compra
        precio_costo REAL,  -- Precio de costo del producto
        nro_referencia TEXT NOT NULL,  -- Número de referencia de la compra
        FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id),  -- Clave foránea que referencia al proveedor
        FOREIGN KEY (producto_id) REFERENCES Productos(id)  -- Clave foránea que referencia al producto
    )
    ''')

    # Tabla de Devoluciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Devoluciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único de la devolución
        factura_id TEXT NOT NULL,  -- Número de factura de la venta
        producto_id INTEGER,  -- Identificador del producto devuelto
        cantidad INTEGER NOT NULL,  -- Cantidad de productos devueltos
        fecha DATE NOT NULL,  -- Fecha de la devolución
        cliente_id INTEGER,  -- Identificador del cliente que realizó la devolución
        FOREIGN KEY (factura_id) REFERENCES Ventas(factura_id),  -- Clave foránea que referencia a la venta
        FOREIGN KEY (producto_id) REFERENCES Productos(id),  -- Clave foránea que referencia al producto
        FOREIGN KEY (cliente_id) REFERENCES Clientes(id)  -- Clave foránea que referencia al cliente
    )
    ''')

    conn.commit()  # Guarda los cambios en la base de datos
    conn.close()  # Cierra la conexión a la base de datos

if __name__ == "__main__":
    create_tables()  # Crea las tablas si el módulo se ejecuta directamente
