from Objetos.Condicion import Condicion
from Objetos.Producto import Producto
from Objetos.Promocion import Promocion
from Objetos.Supermercado import Supermercado


class DSLSupermercado:
    """Crea objetos mediante builders sin acoplar el modelo a la sintaxis."""

    def __init__(self):
        self._supermercado = Supermercado()
        self._actual = None
        self._finalizado = False
        self.errores = []

    def _guardar_actual(self):
        if self._finalizado:
            raise ValueError("La carga del DSL ya fue finalizada.")
        if self._actual is None:
            return
        actual = self._actual
        self._actual = None
        try:
            actual._guardar()
        except ValueError as error:
            self.errores.append(f"{actual._tipo} {actual._codigo}: {error}")

    def producto(self, codigo):
        self._guardar_actual()
        self._actual = ProductoBuilder(self, codigo)
        return self._actual

    def promocion(self, codigo):
        self._guardar_actual()
        self._actual = PromocionBuilder(self, codigo)
        return self._actual

    def finalizar(self):
        self._guardar_actual()
        self._finalizado = True
        return self._supermercado


class _Builder:
    def __init__(self, dsl, codigo):
        self._dsl = dsl
        self._codigo = codigo
        self._nombre = None

    def _verificar_activo(self):
        if self._dsl._finalizado or self._dsl._actual is not self:
            raise ValueError("Este builder ya fue cerrado.")

    def nombre(self, nombre):
        self._verificar_activo()
        self._nombre = nombre
        return self

    def producto(self, codigo):
        self._verificar_activo()
        return self._dsl.producto(codigo)

    def promocion(self, codigo):
        self._verificar_activo()
        return self._dsl.promocion(codigo)

    def finalizar(self):
        self._verificar_activo()
        return self._dsl.finalizar()


class ProductoBuilder(_Builder):
    _tipo = "Producto"

    def __init__(self, dsl, codigo):
        super().__init__(dsl, codigo)
        self._precio = None
        self._categoria = None

    def precio(self, precio):
        self._verificar_activo()
        self._precio = precio
        return self

    def categoria(self, categoria):
        self._verificar_activo()
        self._categoria = categoria
        return self

    def _guardar(self):
        producto = Producto(self._codigo, self._nombre, self._precio, self._categoria)
        self._dsl._supermercado.agregar_producto(producto)


class PromocionBuilder(_Builder):
    _tipo = "Promoción"

    def __init__(self, dsl, codigo):
        super().__init__(dsl, codigo)
        self._descuento = None
        self._condiciones = []

    def descuento(self, porcentaje):
        self._verificar_activo()
        self._descuento = porcentaje
        return self

    def cuando_producto(self, codigo):
        self._verificar_activo()
        condicion = CondicionBuilder(self, codigo)
        self._condiciones.append(condicion)
        return condicion

    def _guardar(self):
        condiciones = [c._construir() for c in self._condiciones]
        promocion = Promocion(self._codigo, self._nombre, condiciones, self._descuento)
        self._dsl._supermercado.agregar_promocion(promocion)


class CondicionBuilder:
    def __init__(self, promocion, codigo):
        self._promocion = promocion
        self._codigo = codigo
        self._operador = "="
        self._cantidad = 1

    def cantidad_igual(self, cantidad):
        self._promocion._verificar_activo()
        self._operador = "="
        self._cantidad = cantidad
        return self

    def cantidad_mayor_igual(self, cantidad):
        self._promocion._verificar_activo()
        self._operador = ">="
        self._cantidad = cantidad
        return self

    def nombre(self, nombre):
        return self._promocion.nombre(nombre)

    def descuento(self, porcentaje):
        return self._promocion.descuento(porcentaje)

    def cuando_producto(self, codigo):
        return self._promocion.cuando_producto(codigo)

    def producto(self, codigo):
        return self._promocion.producto(codigo)

    def promocion(self, codigo):
        return self._promocion.promocion(codigo)

    def finalizar(self):
        return self._promocion.finalizar()

    def _construir(self):
        return Condicion(self._codigo, self._operador, self._cantidad)
