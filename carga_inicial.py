from DSL.Interno.DSLInterno import DSLSupermercado


def cargar_supermercado():
    """Única configuración inicial; devuelve el modelo y la lista de errores."""
    dsl = DSLSupermercado()
    supermercado = (
        dsl
        .producto(1)
            .nombre("Arroz")
            .precio(50)
            .categoria("Comestible")
        .producto(2)
            .nombre("Harina")
            .precio(30)
        .producto(3)
            .categoria("Bebida")
            .precio(100)
            .nombre("Refresco")
        .promocion(1)
            .nombre("Harina x5")
            .cuando_producto(2)
                .cantidad_mayor_igual(5)
            .descuento(20)
        .producto(4)
            .precio(150)
            .nombre("Pizza")
        .promocion(2)
            .descuento(25)
            .cuando_producto(3)
            .cuando_producto(4)
                .cantidad_igual(2)
            .nombre("2 pizzas + refresco")
        .finalizar()
    )
    return supermercado, dsl.errores


if __name__ == "__main__":
    supermercado, errores = cargar_supermercado()
    for error in errores:
        print(f"Error: {error}")
    for producto in supermercado.productos.values():
        print(f"Producto {producto.idProducto}: {producto.nombreProducto}, "
              f"${producto.precioProducto:.2f}, categoría: {producto.categoriaProducto or ''}")
    for promocion in supermercado.promociones.values():
        print(f"Promoción {promocion.codigoPromocion}: {promocion.nombrePromocion}, "
              f"{promocion.porcentajeDescuento}%")
        for condicion in promocion.listaCondiciones:
            print(f"  Producto {condicion.codigoProducto}: "
                  f"cantidad {condicion.operador} {condicion.cantidad}")
