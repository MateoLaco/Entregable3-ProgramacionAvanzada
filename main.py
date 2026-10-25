from DSL.Externo.DSLCompras import ejecutar_compras
from DSL.Externo.DSLMantenimiento import ejecutar_mantenimiento
from carga_inicial import cargar_supermercado


def leer_archivo():
    ruta = input("Ruta del archivo: ").strip().strip('"')
    try:
        with open(ruta, encoding="utf-8-sig") as archivo:
            return archivo.read()
    except OSError as error:
        print(f"No se pudo leer el archivo: {error}")
        return None


def mostrar_resultado(mensajes, errores):
    for mensaje in mensajes:
        print(f"  {mensaje}")
    if errores:
        print(f"\nSe encontraron {len(errores)} error(es):")
        for error in errores:
            print(f"  - {error}")


def mantenimiento(supermercado):
    texto = leer_archivo()
    if texto is not None:
        mostrar_resultado(*ejecutar_mantenimiento(supermercado, texto))


def realizar_compras(supermercado):
    texto = leer_archivo()
    if texto is not None:
        mostrar_resultado(*ejecutar_compras(supermercado, texto))


def listar_productos(supermercado):
    if not supermercado.productos:
        print("No hay productos.")
        return
    print(f"{'Código':>6}  {'Nombre':<20} {'Precio':>10}  Categoría")
    for p in supermercado.productos.values():
        print(f"{p.idProducto:>6}  {p.nombreProducto:<20} {p.precioProducto:>10.2f}  "
              f"{p.categoriaProducto or ''}")


def listar_promociones(supermercado):
    if not supermercado.promociones:
        print("No hay promociones.")
        return
    for promo in supermercado.promociones.values():
        print(f"Promoción {promo.codigoPromocion}: {promo.nombrePromocion} "
              f"({promo.porcentajeDescuento}% de descuento)")
        for c in promo.listaCondiciones:
            nombre = supermercado.productos[c.codigoProducto].nombreProducto
            print(f"    Producto {c.codigoProducto} ({nombre}) cantidad {c.operador} {c.cantidad}")


def listar_compras(supermercado):
    if not supermercado.compras:
        print("No hay compras.")
        return
    for numero, compra in enumerate(supermercado.compras, start=1):
        print(f"\n=== Compra {numero} ===")
        print(f"{'Código':>6}  {'Nombre':<20} {'Cant.':>5} {'P. unit.':>10} {'Desc.':>7} {'Importe':>10}")
        for l in compra.listaLinea:
            print(f"{l.codigoProducto:>6}  {l.nombreProducto:<20} {l.cantidad:>5} "
                  f"{l.precio:>10.2f} {str(l.porcentajeDescuento) + '%':>7} {l.importe:>10.2f}")
        if compra.promocionesAplicadas:
            print("Promociones aplicadas:")
            for codigo, nombre in compra.promocionesAplicadas:
                print(f"    {codigo} - {nombre}")
        else:
            print("Promociones aplicadas: ninguna")
        print(f"Importe total: ${compra.importeTotal:.2f}")


OPCIONES = {
    "1": ("Mantenimiento de productos y promociones", mantenimiento),
    "2": ("Realizar compras", realizar_compras),
    "3": ("Ver lista de productos", listar_productos),
    "4": ("Ver lista de promociones", listar_promociones),
    "5": ("Ver lista de compras", listar_compras),
}


def main():
    supermercado, errores = cargar_supermercado()
    print("Carga inicial realizada.")
    for error in errores:
        print(f"  Error en carga inicial: {error}")

    while True:
        print("\n===== SUPERMERCADO =====")
        for clave, (texto, _) in OPCIONES.items():
            print(f"{clave}. {texto}")
        print("0. Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            break
        if opcion not in OPCIONES:
            print("Opción inválida.")
            continue
        print()
        OPCIONES[opcion][1](supermercado)


if __name__ == "__main__":
    main()
