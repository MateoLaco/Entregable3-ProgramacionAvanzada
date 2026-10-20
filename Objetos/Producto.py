class Producto:
    def __init__(self, idProducto, nombreProducto, precioProducto):
        self.idProducto = idProducto
        self.nombreProducto = nombreProducto
        self.precioProducto = precioProducto
        self.categoriaProducto = None

    def __init__(self, idProducto, nombreProducto, precioProducto, categoriaProducto):
        self.idProducto = idProducto
        self.nombreProducto = nombreProducto
        self.precioProducto = precioProducto
        self.categoriaProducto = categoriaProducto