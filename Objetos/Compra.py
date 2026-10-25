from decimal import Decimal, ROUND_HALF_UP


class LineaCompra:
    def __init__(self, codigoProducto, nombreProducto, precio, cantidad, porcentajeDescuento):
        self.codigoProducto = codigoProducto
        self.nombreProducto = nombreProducto
        self.precio = precio
        self.cantidad = cantidad
        self.porcentajeDescuento = porcentajeDescuento
        bruto = precio * cantidad
        descuento = bruto * porcentajeDescuento / 100
        self.importe = (bruto - descuento).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class Compra:
    def __init__(self, listaLinea, promocionesAplicadas):
        if not listaLinea:
            raise ValueError("La compra debe tener al menos un producto.")
        self.listaLinea = listaLinea
        # Lista de (código, nombre) de las promociones aplicadas
        self.promocionesAplicadas = promocionesAplicadas
        self.importeTotal = sum((linea.importe for linea in listaLinea), Decimal("0"))
