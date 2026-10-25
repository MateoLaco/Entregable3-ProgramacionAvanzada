from decimal import Decimal

from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput

from aplicar_promociones import calcular_compra

gramatica_compras = r"""
    start  : compra*
    compra : "COMPRA" linea* "FIN"
    linea  : "PRODUCTO" NUMERO ("CANTIDAD" NUMERO)?

    NUMERO : /\d+(\.\d+)?/

    %import common.WS
    %ignore WS
"""

parser_compras = Lark(
    gramatica_compras,
    start="start",
    parser="lalr",
)


class _ArmarCompras(Transformer):
    """Convierte el árbol de Lark en una lista de compras [(código, cantidad), ...]."""

    def NUMERO(self, token):
        return Decimal(token) if "." in token else int(token)

    def linea(self, hijos):
        if len(hijos) == 1:
            return (hijos[0], 1)
        return (hijos[0], hijos[1])

    def compra(self, hijos):
        return hijos

    def start(self, hijos):
        return hijos


def ejecutar_compras(supermercado, texto):
    """Devuelve (mensajes, errores). Cada compra con error se descarta sin frenar las demás."""
    try:
        compras = _ArmarCompras().transform(parser_compras.parse(texto))
    except UnexpectedInput as error:
        return [], [f"Error de sintaxis en línea {error.line}, columna {error.column}:\n"
                    f"{error.get_context(texto).rstrip()}"]

    mensajes, errores = [], []
    for numero, items in enumerate(compras, start=1):
        try:
            compra = calcular_compra(supermercado, items)
            supermercado.registrar_compra(compra)
            mensajes.append(f"Compra {numero} del archivo: OK, total ${compra.importeTotal:.2f}")
        except ValueError as error:
            errores.append(f"Compra {numero} del archivo: {error}")
    return mensajes, errores
