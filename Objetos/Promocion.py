from Objetos.Condicion import Condicion
from validaciones import entero, numero, texto


class Promocion:
    def __init__(self, codigoPromocion, nombrePromocion, listaCondiciones, porcentajeDescuento):
        entero(codigoPromocion, "Código de promoción")
        texto(nombrePromocion, "Nombre de promoción")
        condiciones = list(listaCondiciones)
        if not condiciones or any(not isinstance(c, Condicion) for c in condiciones):
            raise ValueError("La promoción debe tener al menos una condición válida.")
        codigos = [c.codigoProducto for c in condiciones]
        if len(codigos) != len(set(codigos)):
            raise ValueError("Una promoción no puede repetir un producto en sus condiciones.")
        porcentajeDescuento = numero(porcentajeDescuento, "Descuento")
        if not 0 <= porcentajeDescuento <= 100:
            raise ValueError("El descuento debe estar entre 0 y 100.")
        self.codigoPromocion = codigoPromocion
        self.nombrePromocion = nombrePromocion
        self.listaCondiciones = condiciones
        self.porcentajeDescuento = porcentajeDescuento
