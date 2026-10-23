from lark import Lark, Transformer

gramatica_mantenimiento = """
    inicio : instruccion+
    instruccion : "AGREGAR" "PRODUCTO" INT "NOMBRE" STRING "PRECIO" NUMBER "FIN"

    %import common.INT
    %import common.NUMBER
    %import common.ESCAPER_STRING -> STRING
    %import common.WS
    %ignore WS
"""

parser_compras = Lark(
    gramatica_mantenimiento,
    start = "inicio",
    parser = "lalr",
)
