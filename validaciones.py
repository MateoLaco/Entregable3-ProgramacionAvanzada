from decimal import Decimal, InvalidOperation


def entero(valor, campo):
    if type(valor) is not int:
        raise ValueError(f"{campo} debe ser un número entero.")


def texto(valor, campo):
    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser texto.")


def numero(valor, campo):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise ValueError(f"{campo} debe ser un número.")
    try:
        resultado = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"{campo} debe ser un número válido.") from None
    if not resultado.is_finite():
        raise ValueError(f"{campo} debe ser un número finito.")
    return resultado
