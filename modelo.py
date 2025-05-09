from datetime import datetime

class Producto:
    def __init__(self, nombre, codigo, vencimiento, precio, cantidad, medida, unidad):
        self.nombre = nombre
        self.codigo = codigo
        self.vencimiento = vencimiento
        self.precio = precio
        self.cantidad = cantidad
        self.medida = medida
        self.unidad = unidad

    def __str__(self):
        return f"{self.nombre} ({self.codigo}): {self.cantidad} {self.unidad} a {self.precio}"

    def actualizar_cantidad(self, cantidad_vendida):
        self.cantidad -= cantidad_vendida


class Venta:
    def __init__(self, producto, cantidad, medida, unidad):
        self.producto = producto
        self.cantidad = cantidad
        self.medida = medida
        self.unidad = unidad
        self.fecha = datetime.now()

    def __str__(self):
        return f"{self.producto.nombre} ({self.producto.codigo}) - {self.cantidad} {self.medida} {self.unidad} en {self.fecha.strftime('%d-%m-%Y')}"

