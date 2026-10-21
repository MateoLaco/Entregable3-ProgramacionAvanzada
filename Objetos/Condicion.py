from Objetos.validaciones import entero


class Condicion:
    def __init__(self, codigoProducto, operador="=", cantidad=1):
        entero(codigoProducto, "Código de producto")
        entero(cantidad, "Cantidad")
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")
        if operador not in ("=", ">="):
            raise ValueError("El operador debe ser '=' o '>='.")
        self.codigoProducto = codigoProducto
        self.operador = operador
        self.cantidad = cantidad
