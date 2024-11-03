# factura_pdf.py
import os
import pdfkit

class Factura:
    """
    Clase para generar un PDF de la factura
    """
    def __init__(self, venta):
        self.venta = venta

    def generar_pdf(self, tax, ruta_facturas):
        """
        Genera un PDF de la factura
        :param tax: Impuesto a aplicar a la venta
        :param ruta_facturas: Ruta donde se guardará el PDF
        :return: None
        """
        # Crear el directorio de facturas si no existe
        if not os.path.exists(ruta_facturas):
            os.makedirs(ruta_facturas)

        # Generar el nombre del archivo PDF
        nombre_archivo = f"{self.venta.factura_id}.pdf"
        ruta_completa = os.path.join(ruta_facturas, nombre_archivo)

        # Generar el contenido HTML de la factura
        html = f"""
        <h1>Factura</h1>
        <p>Fecha: {self.venta.fecha}</p>
        <p>Factura Nro.: {self.venta.factura_id}</p>
        <p>Cliente: {self.venta.cliente.nombre}</p>
        <p>Productos:</p>
        <ul>
            {"".join([f"<li>{p.nombre} - {p.cantidad} x {p.precio}</li>" for p in self.venta.productos])}
        </ul>
        <p>Sub-Total: ${self.venta.total}</p>
        <p>Impuesto: ${(self.venta.total * tax) + self.venta.total}</p>
        <p>Total: ${self.venta.total}</p>
        """

        # Generar el PDF a partir del HTML
        pdfkit.from_string(html, ruta_completa)

