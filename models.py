# models.py
from database import create_connection

class Model:
    """
    Clase base para los modelos de la aplicación.
    Define métodos comunes para guardar, actualizar y eliminar registros.
    """
    def save(self):
        """
        Guarda el objeto en la base de datos.
        Debe ser implementado por las clases derivadas.
        """
        raise NotImplementedError

    def update(self):
        """
        Actualiza el objeto en la base de datos.
        Debe ser implementado por las clases derivadas.
        """
        raise NotImplementedError

    def delete(self):
        """
        Elimina el objeto de la base de datos.
        Debe ser implementado por las clases derivadas.
        """
        raise NotImplementedError

class Producto(Model):
    """
    Modelo para representar un producto en la base de datos.
    """
    def __init__(self, nombre, descripcion, precio, stock, id=None):
        """
        Constructor de la clase Producto.

        Args:
            nombre (str): Nombre del producto.
            descripcion (str): Descripción del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad en stock del producto.
            id (int, optional): ID del producto en la base de datos. Defaults to None.
        """
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio
        self.stock = stock

    def save(self):
        """
        Guarda un nuevo producto en la base de datos.

        Raises:
            ValueError: Si el precio o el stock son negativos.
        """
        if self.precio < 0 or self.stock < 0:
            raise ValueError("El precio y el stock deben ser números positivos.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Productos (nombre, descripcion, precio, stock)
        VALUES (?, ?, ?, ?)
        ''', (self.nombre, self.descripcion, self.precio, self.stock))
        conn.commit()
        conn.close()

    def update(self):
        """
        Actualiza un producto existente en la base de datos.

        Raises:
            ValueError: Si el ID del producto no está definido o si el precio o el stock son negativos.
        """
        if self.id is None:
            raise ValueError("El ID del producto no está definido.")
        if self.precio < 0 or self.stock < 0:
            raise ValueError("El precio y el stock deben ser números positivos.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Productos SET nombre=?, descripcion=?, precio=?, stock=? WHERE id=?
        ''', (self.nombre, self.descripcion, self.precio, self.stock, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina un producto de la base de datos.

        Raises:
            ValueError: Si el ID del producto no está definido.
        """
        if self.id is None:
            raise ValueError("El ID del producto no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Productos WHERE id=?
        ''', (self.id,))
        conn.commit()
        conn.close()

class Cliente(Model):
    """
    Modelo para representar un cliente en la base de datos.
    """
    def __init__(self, nombre, telefono, email, id=None):
        """
        Constructor de la clase Cliente.

        Args:
            nombre (str): Nombre del cliente.
            telefono (str): Número de teléfono del cliente.
            email (str): Dirección de correo electrónico del cliente.
            id (int, optional): ID del cliente en la base de datos. Defaults to None.
        """
        self.id = id
        self.nombre = nombre
        self.telefono = telefono
        self.email = email

    def save(self):
        """
        Guarda un nuevo cliente en la base de datos.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Clientes (nombre, telefono, email)
        VALUES (?, ?, ?)
        ''', (self.nombre, self.telefono, self.email))
        conn.commit()
        conn.close()

    def update(self):
        """
        Actualiza un cliente existente en la base de datos.

        Raises:
            ValueError: Si el ID del cliente no está definido.
        """
        if self.id is None:
            raise ValueError("El ID del cliente no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Clientes SET nombre=?, telefono=?, email=? WHERE id=?
        ''', (self.nombre, self.telefono, self.email, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina un cliente de la base de datos.

        Raises:
            ValueError: Si el ID del cliente no está definido.
        """
        if self.id is None:
            raise ValueError("El ID del cliente no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Clientes WHERE id=?
        ''', (self.id,))
        conn.commit()
        conn.close()

class Proveedor(Model):
    """
    Modelo para representar un proveedor en la base de datos.
    """
    def __init__(self, nombre, telefono, email, id=None):
        """
        Constructor de la clase Proveedor.

        Args:
            nombre (str): Nombre del proveedor.
            telefono (str): Número de teléfono del proveedor.
            email (str): Dirección de correo electrónico del proveedor.
            id (int, optional): ID del proveedor en la base de datos. Defaults to None.
        """
        self.id = id
        self.nombre = nombre
        self.telefono = telefono
        self.email = email

    def save(self):
        """
        Guarda un nuevo proveedor en la base de datos.
        """
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO Proveedores (nombre, telefono, email)
        VALUES (?, ?, ?)
        ''', (self.nombre, self.telefono, self.email))
        conn.commit()
        conn.close()

    def update(self):
        """
        Actualiza un proveedor existente en la base de datos.

        Raises:
            ValueError: Si el ID del proveedor no está definido.
        """
        if self.id is None:
            raise ValueError("El ID del proveedor no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Proveedores SET nombre=?, telefono=?, email=? WHERE id=?
        ''', (self.nombre, self.telefono, self.email, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina un proveedor de la base de datos.

        Raises:
            ValueError: Si el ID del proveedor no está definido.
        """
        if self.id is None:
            raise ValueError("El ID del proveedor no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Proveedores WHERE id=?
        ''', (self.id,))
        conn.commit()
        conn.close()

class Venta(Model):
    """
    Modelo para representar una venta en la base de datos.
    """
    def __init__(self, cliente_id, producto_id, cantidad, fecha, factura_id, id=None):
        """
        Constructor de la clase Venta.

        Args:
            cliente_id (int): ID del cliente que realizó la compra.
            producto_id (int): ID del producto vendido.
            cantidad (int): Cantidad de productos vendidos.
            fecha (str): Fecha de la venta.
            factura_id (str): Número de factura de la venta.
            id (int, optional): ID de la venta en la base de datos. Defaults to None.
        """
        self.id = id
        self.cliente_id = cliente_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.fecha = fecha
        self.factura_id = factura_id

    def save(self, cursor=None):
        """
        Guarda una nueva venta en la base de datos.

        Args:
            cursor (sqlite3.Cursor, optional): Cursor de la base de datos. Defaults to None.

        Raises:
            ValueError: Si la cantidad es negativa.
        """
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = cursor or conn.cursor()
        cursor.execute('''
        INSERT INTO Ventas (cliente_id, producto_id, cantidad, fecha, factura_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.cliente_id, self.producto_id, self.cantidad, self.fecha, self.factura_id))
        if cursor is None:
            conn.commit()
            conn.close()

    def update(self):
        """
        Actualiza una venta existente en la base de datos.

        Raises:
            ValueError: Si el ID de la venta no está definido o si la cantidad es negativa.
        """
        if self.id is None:
            raise ValueError("El ID de la venta no está definido.")
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Ventas SET cliente_id=?, producto_id=?, cantidad=?, fecha=?, factura_id=? WHERE id=?
        ''', (self.cliente_id, self.producto_id, self.cantidad, self.fecha, self.factura_id, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina una venta de la base de datos.

        Raises:
            ValueError: Si el ID de la venta no está definido.
        """
        if self.id is None:
            raise ValueError("El ID de la venta no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Ventas WHERE id=?
        ''', (self.id,))
        conn.commit()
        conn.close()

class Compra(Model):
    """
    Modelo para representar una compra en la base de datos.
    """
    def __init__(self, proveedor_id, producto_id, cantidad, fecha, precio_costo=None, nro_referencia=None, id=None):
        """
        Constructor de la clase Compra.

        Args:
            proveedor_id (int): ID del proveedor que suministró los productos.
            producto_id (int): ID del producto comprado.
            cantidad (int): Cantidad de productos comprados.
            fecha (str): Fecha de la compra.
            precio_costo (float, optional): Precio de costo del producto. Defaults to None.
            nro_referencia (str, optional): Número de referencia de la compra. Defaults to None.
            id (int, optional): ID de la compra en la base de datos. Defaults to None.
        """
        self.id = id
        self.proveedor_id = proveedor_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.fecha = fecha
        self.precio_costo = precio_costo
        self.nro_referencia = nro_referencia

    def save(self, cursor=None):
        """
        Guarda una nueva compra en la base de datos.

        Args:
            cursor (sqlite3.Cursor, optional): Cursor de la base de datos. Defaults to None.

        Raises:
            ValueError: Si la cantidad es negativa.
        """
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = cursor or conn.cursor()
        if self.id:
            cursor.execute("""
                UPDATE Compras
                SET proveedor_id=?, producto_id=?, cantidad=?, fecha=?, precio_costo=?, nro_referencia=?
                WHERE id=?
            """, (self.proveedor_id, self.producto_id, self.cantidad, self.fecha, self.precio_costo, self.nro_referencia, self.id))
        else:
            cursor.execute("""
                INSERT INTO Compras (proveedor_id, producto_id, cantidad, fecha, precio_costo, nro_referencia)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.proveedor_id, self.producto_id, self.cantidad, self.fecha, self.precio_costo, self.nro_referencia))
            self.id = cursor.lastrowid
        if cursor is None:
            conn.commit()
            conn.close()

    def update(self):
        """
        Actualiza una compra existente en la base de datos.

        Raises:
            ValueError: Si el ID de la compra no está definido o si la cantidad es negativa.
        """
        if self.id is None:
            raise ValueError("El ID de la compra no está definido.")
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = conn.cursor()
        self.save(cursor)
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina una compra de la base de datos.

        Raises:
            ValueError: Si el ID de la compra no está definido.
        """
        if self.id is None:
            raise ValueError("El ID de la compra no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Compras WHERE id=?", (self.id,))
        conn.commit()
        conn.close()

class Devolucion(Model):
    """
    Modelo para representar una devolución en la base de datos.
    """
    def __init__(self, factura_id, producto_id, cantidad, fecha, cliente_id=None, id=None):
        """
        Constructor de la clase Devolucion.

        Args:
            factura_id (str): Número de factura de la venta.
            producto_id (int): ID del producto devuelto.
            cantidad (int): Cantidad de productos devueltos.
            fecha (str): Fecha de la devolución.
            cliente_id (int, optional): ID del cliente que realizó la devolución. Defaults to None.
            id (int, optional): ID de la devolución en la base de datos. Defaults to None.
        """
        self.id = id
        self.factura_id = factura_id
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.fecha = fecha
        self.cliente_id = cliente_id

    def save(self, cursor=None):
        """
        Guarda una nueva devolución en la base de datos.

        Args:
            cursor (sqlite3.Cursor, optional): Cursor de la base de datos. Defaults to None.

        Raises:
            ValueError: Si la cantidad es negativa.
        """
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = cursor or conn.cursor()
        cursor.execute('''
        INSERT INTO Devoluciones (factura_id, producto_id, cantidad, fecha, cliente_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.factura_id, self.producto_id, self.cantidad, self.fecha, self.cliente_id))
        if cursor is None:
            conn.commit()
            conn.close()

    def update(self):
        """
        Actualiza una devolución existente en la base de datos.

        Raises:
            ValueError: Si el ID de la devolución no está definido o si la cantidad es negativa.
        """
        if self.id is None:
            raise ValueError("El ID de la devolución no está definido.")
        if self.cantidad < 0:
            raise ValueError("La cantidad debe ser un número positivo.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE Devoluciones SET factura_id=?, producto_id=?, cantidad=?, fecha=?, cliente_id=? WHERE id=?
        ''', (self.factura_id, self.producto_id, self.cantidad, self.fecha, self.cliente_id, self.id))
        conn.commit()
        conn.close()

    def delete(self):
        """
        Elimina una devolución de la base de datos.

        Raises:
            ValueError: Si el ID de la devolución no está definido.
        """
        if self.id is None:
            raise ValueError("El ID de la devolución no está definido.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM Devoluciones WHERE id=?
        ''', (self.id,))
        conn.commit()
        conn.close()
