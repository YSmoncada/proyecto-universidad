from datetime import datetime
from modelo import *

productos = []  
ventas = []

def agregar_producto(nombre, codigo, vencimiento, precio, cantidad, medida, unidad):
    if any(p.codigo == codigo for p in productos):
        raise ValueError("Ya existe un producto con ese código.")
    nuevo = Producto(nombre, codigo, vencimiento, precio, cantidad, medida, unidad)

    productos.append(nuevo)


def obtener_productos():
    return productos

def obtener_producto_por_nombre(nombre):
    for producto in productos:
        if producto.nombre.lower() == nombre.lower():
            return producto
    return None

def vender_producto(nombre, cantidad, medida, unidad):
    producto = obtener_producto_por_nombre(nombre)
    if producto is None:
        raise ValueError("Producto no encontrado.")

    if producto.cantidad < cantidad:
        raise ValueError("Cantidad insuficiente en inventario.")

    producto.cantidad -= cantidad
    ventas.append(Venta(producto, cantidad, medida, unidad))

def obtener_ventas():
    return [{
        "nombre": v.producto.nombre,
        "unidad": v.unidad,
        "medida": v.medida,
        "cantidad": v.cantidad,
        "fecha": v.fecha.strftime("%d-%m-%Y %H:%M:%S")
    } for v in ventas]

def obtener_ventas_totales():
    return sum(v.producto.precio * v.cantidad for v in ventas)

def calcular_impuesto_anual(total_ventas):
    return total_ventas * 7 / 1000

def eliminar_producto_por_codigo(codigo):
    global productos
    for i, p in enumerate(productos):
        if p.codigo == codigo:
            del productos[i]
            return True
    return False







