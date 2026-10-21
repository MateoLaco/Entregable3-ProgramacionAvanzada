from Objetos.Producto import Producto
from Objetos.Promocion import Promocion


class Supermercado:
    """Modelo compartido por el DSL interno y los futuros DSL externos."""

    def __init__(self):
        self.productos = {}
        self.promociones = {}
        self.compras = []

    def agregar_producto(self, producto):
        if not isinstance(producto, Producto):
            raise ValueError("Se esperaba un Producto.")
        if producto.idProducto in self.productos:
            raise ValueError(f"Ya existe el producto {producto.idProducto}.")
        self.productos[producto.idProducto] = producto

    def agregar_promocion(self, promocion):
        if not isinstance(promocion, Promocion):
            raise ValueError("Se esperaba una Promocion.")
        if promocion.codigoPromocion in self.promociones:
            raise ValueError(f"Ya existe la promoción {promocion.codigoPromocion}.")
        for condicion in promocion.listaCondiciones:
            if condicion.codigoProducto not in self.productos:
                raise ValueError(f"No existe el producto {condicion.codigoProducto} de la promoción.")
        self.promociones[promocion.codigoPromocion] = promocion
