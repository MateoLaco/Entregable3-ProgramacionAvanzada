from decimal import Decimal

from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput

from Objetos.Condicion import Condicion
from Objetos.Producto import Producto
from Objetos.Promocion import Promocion

gramatica_mantenimiento = r"""
    start : instruccion*

    ?instruccion : agregar_producto
                 | actualizar_producto
                 | eliminar_producto
                 | agregar_promocion
                 | actualizar_promocion
                 | eliminar_promocion

    agregar_producto     : "AGREGAR" "PRODUCTO" NUMERO campo_producto* "FIN"
    actualizar_producto  : "ACTUALIZAR" "PRODUCTO" NUMERO campo_producto* "FIN"
    eliminar_producto    : "ELIMINAR" "PRODUCTO" NUMERO
    agregar_promocion    : "AGREGAR" "PROMOCION" NUMERO campo_promocion* "FIN"
    actualizar_promocion : "ACTUALIZAR" "PROMOCION" NUMERO campo_promocion* "FIN"
    eliminar_promocion   : "ELIMINAR" "PROMOCION" NUMERO

    campo_producto : "NOMBRE" TEXTO       -> nombre
                   | "PRECIO" NUMERO      -> precio
                   | "CATEGORIA" TEXTO    -> categoria

    campo_promocion : "NOMBRE" TEXTO      -> nombre
                    | "DESCUENTO" NUMERO  -> descuento
                    | "CUANDO" condicion+ -> cuando

    condicion : "PRODUCTO" NUMERO ("CANTIDAD" OPERADOR NUMERO)?

    OPERADOR : ">=" | "="
    NUMERO   : /\d+(\.\d+)?/
    TEXTO    : /"[^"\n]*"/ | /“[^”\n]*”/

    %import common.WS
    %ignore WS
"""

parser_mantenimiento = Lark(
    gramatica_mantenimiento,
    start="start",
    parser="lalr",
)


class _ArmarInstrucciones(Transformer):
    # Convierte el árbol de Lark en tuplas (acción, código, datos).

    def NUMERO(self, token):
        return Decimal(token) if "." in token else int(token)

    def TEXTO(self, token):
        return str(token)[1:-1]

    def OPERADOR(self, token):
        return str(token)

    def nombre(self, hijos):
        return ("nombre", hijos[0])

    def precio(self, hijos):
        return ("precio", hijos[0])

    def categoria(self, hijos):
        return ("categoria", hijos[0])

    def descuento(self, hijos):
        return ("descuento", hijos[0])

    def cuando(self, hijos):
        return ("condiciones", hijos)

    def condicion(self, hijos):
        if len(hijos) == 1:
            return (hijos[0], "=", 1)
        return tuple(hijos)

    def agregar_producto(self, hijos):
        return ("agregar_producto", hijos[0], dict(hijos[1:]))

    def actualizar_producto(self, hijos):
        return ("actualizar_producto", hijos[0], dict(hijos[1:]))

    def eliminar_producto(self, hijos):
        return ("eliminar_producto", hijos[0], {})

    def agregar_promocion(self, hijos):
        return ("agregar_promocion", hijos[0], dict(hijos[1:]))

    def actualizar_promocion(self, hijos):
        return ("actualizar_promocion", hijos[0], dict(hijos[1:]))

    def eliminar_promocion(self, hijos):
        return ("eliminar_promocion", hijos[0], {})

    def start(self, hijos):
        return hijos


def _armar_condiciones(datos):
    if "condiciones" in datos:
        datos["condiciones"] = [Condicion(*c) for c in datos["condiciones"]]
    return datos


def _agregar_producto(supermercado, codigo, datos):
    supermercado.agregar_producto(
        Producto(codigo, datos.get("nombre"), datos.get("precio"), datos.get("categoria")))


def _actualizar_producto(supermercado, codigo, datos):
    supermercado.actualizar_producto(codigo, **datos)


def _eliminar_producto(supermercado, codigo, datos):
    supermercado.eliminar_producto(codigo)


def _agregar_promocion(supermercado, codigo, datos):
    datos = _armar_condiciones(datos)
    supermercado.agregar_promocion(
        Promocion(codigo, datos.get("nombre"), datos.get("condiciones", []), datos.get("descuento")))


def _actualizar_promocion(supermercado, codigo, datos):
    supermercado.actualizar_promocion(codigo, **_armar_condiciones(datos))


def _eliminar_promocion(supermercado, codigo, datos):
    supermercado.eliminar_promocion(codigo)


_ACCIONES = {
    "agregar_producto": ("Agregar producto", _agregar_producto),
    "actualizar_producto": ("Actualizar producto", _actualizar_producto),
    "eliminar_producto": ("Eliminar producto", _eliminar_producto),
    "agregar_promocion": ("Agregar promoción", _agregar_promocion),
    "actualizar_promocion": ("Actualizar promoción", _actualizar_promocion),
    "eliminar_promocion": ("Eliminar promoción", _eliminar_promocion),
}


def ejecutar_mantenimiento(supermercado, texto):
    # Devuelve (mensajes, errores). Un error sintáctico impide ejecutar el archivo.
    # Un error semántico descarta solo esa instrucción y permite continuar.
    try:
        instrucciones = _ArmarInstrucciones().transform(parser_mantenimiento.parse(texto))
    except UnexpectedInput as error:
        return [], [f"Error de sintaxis en línea {error.line}, columna {error.column}:\n"
                    f"{error.get_context(texto).rstrip()}"]

    mensajes, errores = [], []
    for accion, codigo, datos in instrucciones:
        descripcion, ejecutar = _ACCIONES[accion]
        try:
            ejecutar(supermercado, codigo, datos)
            mensajes.append(f"{descripcion} {codigo}: OK")
        except ValueError as error:
            errores.append(f"{descripcion} {codigo}: {error}")
    return mensajes, errores
