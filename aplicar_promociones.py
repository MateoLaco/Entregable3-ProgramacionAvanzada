from decimal import Decimal

from Objetos.Compra import Compra, LineaCompra
from validaciones import entero


def _se_cumple(promocion, restantes):
    return all(restantes.get(c.codigoProducto, 0) >= c.cantidad
               for c in promocion.listaCondiciones)


def calcular_compra(supermercado, items):
    # Construye una compra a partir de pares (código de producto, cantidad).
    # Aplica las promociones de mayor a menor descuento sobre unidades disponibles.
    # Cada promoción se repite mientras se cumplan todas sus condiciones.
    # Con "= N" se usan N unidades; con ">= N", todas las restantes del producto.
    if not items:
        raise ValueError("La compra debe tener al menos un producto.")

    cantidades = {}
    for codigo, cantidad in items:
        producto = supermercado.buscar_producto(codigo)
        entero(cantidad, f"Cantidad del producto {codigo}")
        if cantidad <= 0:
            raise ValueError(f"La cantidad del producto {codigo} debe ser mayor que cero.")
        cantidades[producto.idProducto] = cantidades.get(producto.idProducto, 0) + cantidad

    restantes = dict(cantidades)
    con_descuento = {}  # (código de producto, porcentaje) -> unidades
    aplicadas = []

    promociones = sorted(supermercado.promociones.values(),
                         key=lambda p: (-p.porcentajeDescuento, p.codigoPromocion))
    for promocion in promociones:
        while _se_cumple(promocion, restantes):
            for condicion in promocion.listaCondiciones:
                codigo = condicion.codigoProducto
                usadas = restantes[codigo] if condicion.operador == ">=" else condicion.cantidad
                restantes[codigo] -= usadas
                clave = (codigo, promocion.porcentajeDescuento)
                con_descuento[clave] = con_descuento.get(clave, 0) + usadas
            if (promocion.codigoPromocion, promocion.nombrePromocion) not in aplicadas:
                aplicadas.append((promocion.codigoPromocion, promocion.nombrePromocion))

    lineas = []
    for codigo in cantidades:
        producto = supermercado.productos[codigo]
        porcentajes = sorted((p for (c, p) in con_descuento if c == codigo), reverse=True)
        for porcentaje in porcentajes:
            lineas.append(LineaCompra(codigo, producto.nombreProducto, producto.precioProducto,
                                      con_descuento[(codigo, porcentaje)], porcentaje))
        if restantes[codigo] > 0:
            lineas.append(LineaCompra(codigo, producto.nombreProducto, producto.precioProducto,
                                      restantes[codigo], Decimal("0")))

    return Compra(lineas, aplicadas)
