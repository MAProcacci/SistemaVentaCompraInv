Sistema de Ventas e Inventario - Inversiones Torino C.A.

Descripción General:

	Este sistema de ventas e inventario está diseñado para gestionar las operaciones diarias de una empresa, incluyendo la gestión de productos, clientes, proveedores, ventas, compras, devoluciones y generación de reportes. El sistema está desarrollado en Python utilizando la biblioteca Flet para la interfaz gráfica y SQLite para la gestión de la base de datos.


Características Principales:

Gestión de Productos:
	Agregar, Modificar y Eliminar Productos: Permite la gestión completa de los productos, incluyendo su nombre, descripción, precio y stock.

Listado de Productos: Muestra una lista de todos los productos disponibles, con opciones de filtrado.

Gestión de Clientes:
	Agregar, Modificar y Eliminar Clientes: Permite la gestión de la información de los clientes, incluyendo su nombre, teléfono y correo electrónico.

Listado de Clientes: Muestra una lista de todos los clientes registrados, con opciones de filtrado.

Gestión de Proveedores:
	Agregar, Modificar y Eliminar Proveedores: Permite la gestión de la información de los proveedores, incluyendo su nombre, teléfono y correo electrónico.

Listado de Proveedores: Muestra una lista de todos los proveedores registrados, con opciones de filtrado.

Gestión de Ventas:
	Registro de Ventas: Permite registrar las ventas realizadas, seleccionando el cliente y los productos vendidos.

Generación de Facturas: Genera automáticamente una factura en formato PDF para cada venta realizada.

Gestión de Compras:
	Registro de Compras: Permite registrar las compras realizadas, seleccionando el proveedor y los productos comprados.

Actualización de Stock: Actualiza automáticamente el stock de los productos después de registrar una compra.

Gestión de Devoluciones:
	Registro de Devoluciones: Permite registrar las devoluciones de productos, actualizando el stock y registrando la devolución en la base de datos.

Reportes y Gráficos:
	Generación de Reportes: Permite generar reportes detallados sobre ventas, compras, devoluciones, productos, clientes y proveedores.

Gráficos Estadísticos: Genera gráficos para visualizar las ventas, compras y devoluciones de manera más intuitiva.

Seguridad y Usuarios:
	Control de Acceso: Implementa un sistema de autenticación de usuarios con diferentes niveles de acceso.

Gestión de Usuarios: Permite al administrador crear, modificar y eliminar usuarios del sistema.

Requisitos del Sistema:

	Python 3.7 o superior

	Biblioteca Flet

	SQLite

	ReportLab (para generación de PDF)

	Matplotlib (para generación de gráficos)

requirements.txt

  flet==0.3.2
  sqlite3
  reportlab==3.6.12
  matplotlib==3.4.3
  cryptography==36.0.1
