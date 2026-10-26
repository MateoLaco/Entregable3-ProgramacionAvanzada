from Objetos.Compra import Compra
from Objetos.Producto import Producto
from Objetos.Promocion import Promocion
from validaciones import entero


class Supermercado:
    # Modelo semántico compartido por el DSL interno y los DSL externos

    def __init__(self):
        self.productos = {}
        self.promociones = {}
        self.compras = []

    # ---------- Productos ----------

    def agregar_producto(self, producto):
        if not isinstance(producto, Producto):
            raise ValueError("Se esperaba un Producto.")
        if producto.idProducto in self.productos:
            raise ValueError(f"Ya existe el producto {producto.idProducto}.")
        self.productos[producto.idProducto] = producto

    def buscar_producto(self, codigo):
        entero(codigo, "Código de producto")
        if codigo not in self.productos:
            raise ValueError(f"No existe el producto {codigo}.")
        return self.productos[codigo]

    def actualizar_producto(self, codigo, **cambios):
        # Los atributos no especificados conservan su valor anterior.
        actual = self.buscar_producto(codigo)
        nuevo = Producto(
            codigo,
            cambios.get("nombre", actual.nombreProducto),
            cambios.get("precio", actual.precioProducto),
            cambios.get("categoria", actual.categoriaProducto),
        )
        self.productos[codigo] = nuevo

    def eliminar_producto(self, codigo):
        self.buscar_producto(codigo)
        for promocion in self.promociones.values():
            if any(c.codigoProducto == codigo for c in promocion.listaCondiciones):
                raise ValueError(
                    f"El producto {codigo} está asociado a la promoción {promocion.codigoPromocion}.")
        del self.productos[codigo]

    # ---------- Promociones ----------

    def _validar_productos_de(self, promocion):
        for condicion in promocion.listaCondiciones:
            if condicion.codigoProducto not in self.productos:
                raise ValueError(f"No existe el producto {condicion.codigoProducto} de la promoción.")

    def agregar_promocion(self, promocion):
        if not isinstance(promocion, Promocion):
            raise ValueError("Se esperaba una Promocion.")
        if promocion.codigoPromocion in self.promociones:
            raise ValueError(f"Ya existe la promoción {promocion.codigoPromocion}.")
        self._validar_productos_de(promocion)
        self.promociones[promocion.codigoPromocion] = promocion

    def buscar_promocion(self, codigo):
        entero(codigo, "Código de promoción")
        if codigo not in self.promociones:
            raise ValueError(f"No existe la promoción {codigo}.")
        return self.promociones[codigo]

    def actualizar_promocion(self, codigo, **cambios):
        # Las condiciones nuevas reemplazan todas las condiciones anteriores.
        actual = self.buscar_promocion(codigo)
        nueva = Promocion(
            codigo,
            cambios.get("nombre", actual.nombrePromocion),
            cambios.get("condiciones", actual.listaCondiciones),
            cambios.get("descuento", actual.porcentajeDescuento),
        )
        self._validar_productos_de(nueva)
        self.promociones[codigo] = nueva

    def eliminar_promocion(self, codigo):
        self.buscar_promocion(codigo)
        del self.promociones[codigo]

    # ---------- Compras ----------

    def registrar_compra(self, compra):
        if not isinstance(compra, Compra):
            raise ValueError("Se esperaba una Compra.")
        self.compras.append(compra)
