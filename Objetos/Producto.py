from validaciones import entero, numero, texto


class Producto:
    def __init__(self, idProducto, nombreProducto, precioProducto, categoriaProducto=None):
        entero(idProducto, "Código de producto")
        texto(nombreProducto, "Nombre de producto")
        precioProducto = numero(precioProducto, "Precio")
        decimales = precioProducto.as_tuple()
        tiene_mas_de_dos_decimales = (
            decimales.exponent < -2 and any(decimales.digits[decimales.exponent + 2:])
            )
        if precioProducto < 0 or tiene_mas_de_dos_decimales:
            raise ValueError("El precio debe ser no negativo y tener hasta dos decimales.")
        if categoriaProducto is not None:
            texto(categoriaProducto, "Categoría")
        self.idProducto = idProducto
        self.nombreProducto = nombreProducto
        self.precioProducto = precioProducto
        self.categoriaProducto = categoriaProducto
