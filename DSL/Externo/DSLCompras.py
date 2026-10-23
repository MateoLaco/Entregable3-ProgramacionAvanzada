from lark import Lark, Transformer

gramatica_compras = """
    inicio : "COMPRA" producto+ "FIN"
    producto : "PRODUCTO" INT "CANTIDAD" INT

    %import common.INT
    %import common.WS
    %ignore WS
"""

parser_compras = Lark(
    gramatica_compras,
    start = "inicio",
    parser = "lalr",
)
