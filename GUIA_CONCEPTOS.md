# Guía de conceptos: Entregable 3 (DSL)

Esta guía explica desde cero los temas del entregable, usando como ejemplo el propio supermercado. Leela en orden, porque cada sección usa lo que explicó la anterior.

---

## 0. El entregable en un párrafo

Hay que hacer un programa de supermercado que guarde **productos** y **promociones** y que registre **compras** aplicando las promociones que correspondan. La gracia del entregable no es el supermercado en sí: lo que se evalúa es **cómo se cargan los datos**. Se cargan de tres formas, cada una con un "mini-lenguaje" propio:

| Para qué | Cómo se escribe | Tipo |
|---|---|---|
| Carga inicial (al arrancar el programa) | Código Python: `.producto(1).nombre("Arroz").precio(50)...` | DSL **interno** |
| Mantenimiento (agregar, modificar o borrar) | Archivo de texto: `AGREGAR PRODUCTO 5 NOMBRE "Azúcar" ... FIN` | DSL **externo** n.º 1 |
| Compras | Archivo de texto: `COMPRA PRODUCTO 2 CANTIDAD 5 ... FIN` | DSL **externo** n.º 2 |

Las tres formas terminan creando **los mismos objetos de Python** (el *modelo semántico*). Ese es el concepto central de todo el entregable.

---

## 1. ¿Qué es un DSL?

**DSL** significa *Domain-Specific Language*, o sea, *lenguaje específico de dominio*. Es un lenguaje pensado para resolver **un solo tipo de problema** y nada más.

Lo contrario es un lenguaje de **propósito general** (Python, Java, C), con el que se puede programar cualquier cosa.

DSL que seguramente ya usaste sin saberlo:

| DSL | Dominio | Ejemplo |
|---|---|---|
| SQL | Consultar bases de datos | `SELECT nombre FROM productos WHERE precio > 50` |
| Expresiones regulares | Buscar patrones en texto | `\d{3}-\d{4}` |
| HTML | Describir páginas web | `<h1>Hola</h1>` |
| CSS | Darle estilo a una página | `h1 { color: red; }` |

Con SQL no se puede escribir un videojuego, pero para consultar datos es mucho más cómodo que Python. **Esa es la idea:** un DSL es limitado a propósito y, a cambio, es muy expresivo dentro de su dominio. Alguien que no programa (por ejemplo, el encargado del supermercado) podría escribir esto sin saber Python:

```
AGREGAR PRODUCTO 5
  NOMBRE "Azúcar"
  PRECIO 60
FIN
```

---

## 2. DSL interno vs. DSL externo

Esta distinción aparece en todo el entregable.

### DSL interno (o embebido)
Es un DSL escrito **dentro de un lenguaje que ya existe**, en este caso Python. Técnicamente es Python común y corriente, pero las clases y los métodos están diseñados para que el código **se lea como una descripción del dominio**:

```python
DSLSupermercado()
    .producto(1)
        .nombre("Arroz")
        .precio(50)
    .finalizar()
```

Eso es Python válido: son llamadas a métodos una detrás de otra. Pero se lee casi como "producto 1, de nombre Arroz y precio 50".

- **Ventaja:** no hay que escribir un parser. Python ya entiende el código.
- **Desventaja:** hay que respetar la sintaxis de Python (puntos, paréntesis, comillas) y hace falta Python para ejecutarlo.

### DSL externo
Es un lenguaje **con sintaxis propia**, que se escribe en un archivo de texto aparte. Python no lo entiende por sí solo, así que hay que **escribir un programa que lo lea** (un *parser*):

```
COMPRA
  PRODUCTO 2 CANTIDAD 5
FIN
```

- **Ventaja:** la sintaxis es libre y puede ser muy simple para alguien que no programa.
- **Desventaja:** hay que definir una gramática, escribir el parser y manejar los errores de sintaxis. Para eso se usan **Lark** o **PLY** (ver secciones 6 y 7).

| | Interno | Externo |
|---|---|---|
| ¿Dónde se escribe? | En el código Python | En un archivo `.txt` aparte |
| ¿Quién lo entiende? | Python directamente | Un parser que escribimos nosotros |
| En el entregable | `carga_inicial.py` | Archivos de mantenimiento y de compras |
| Técnica | Fluent Interface + Expression Builders | Gramática + Lark/PLY |

---

## 3. El modelo semántico (lo más importante)

El **modelo semántico** son las clases que representan el dominio **de verdad**, sin importar cómo se cargaron los datos. En este proyecto son:

- `Producto`: código, nombre, precio y categoría.
- `Promocion`: código, nombre, lista de condiciones y porcentaje de descuento.
- `Condicion`: código de producto, operador (`=` o `>=`) y cantidad.
- `Compra`: líneas, promociones aplicadas e importe total.
- `Supermercado`: el contenedor de todo, con las operaciones `agregar_producto`, `agregar_promocion`, etc.

Todo eso está en la carpeta [Objetos/](Objetos/).

**¿Por qué separarlo de los DSL?** Porque así los tres DSL (el interno y los dos externos) son solo **formas distintas de llegar al mismo lugar**:

```
 carga_inicial.py (DSL interno) ──┐
                                  │
 mantenimiento.txt (DSL externo) ─┼──►  Supermercado / Producto / Promocion   ◄── modelo semántico
                                  │
 compras.txt (DSL externo) ───────┘
```

Consecuencias de esta separación:

1. **Las validaciones van en el modelo, una sola vez.** "El precio tiene que tener 2 decimales como máximo" se controla en `Producto`, y vale para los tres DSL sin repetir código.
2. **Se puede cambiar un DSL sin tocar el resto.** La letra pide que sea "fácil reemplazar el DSL interno por otro". Como el DSL interno solo llama a `supermercado.agregar_producto(...)`, se puede tirar y hacer otro sin que el modelo se entere.
3. **Los errores semánticos los detecta el modelo** (ver sección 8).

> Una regla útil para recordar: **el DSL es la sintaxis, el modelo semántico es el significado.**

---

## 4. Method chaining y Fluent Interface

### Method chaining (encadenamiento de métodos)
Es poder escribir `obj.a().b().c()`. Funciona porque **cada método devuelve un objeto** (normalmente `self`), sobre el que se llama al siguiente:

```python
class Contador:
    def __init__(self):
        self.valor = 0

    def sumar(self, n):
        self.valor += n
        return self          # ← la clave: devolver self

    def restar(self, n):
        self.valor -= n
        return self

Contador().sumar(10).restar(3).sumar(1).valor   # 8
```

Sin el `return self`, `sumar(10)` devolvería `None` y `.restar(3)` daría error.

### Fluent Interface
Es un **estilo de diseño** (el nombre lo puso Martin Fowler) en el que se usa el encadenamiento para que el código **se lea como una oración del dominio**. No alcanza con encadenar: los nombres de los métodos tienen que tener sentido en el dominio. `.cuando_producto(2).cantidad_mayor_igual(5)` se lee como "cuando el producto 2 tenga cantidad mayor o igual a 5". Eso es lo que lo vuelve "fluido".

En Python, como una expresión larga ocupa varias líneas, se la encierra entre paréntesis (fijate en `carga_inicial.py`):

```python
supermercado = (
    dsl
    .producto(1)
        .nombre("Arroz")
    .finalizar()
)
```

La sangría es **solo visual**: a Python no le importa. Sirve para que se vea qué atributo pertenece a qué producto.

---

## 5. Expression Builder

La letra pide "encadenamiento de métodos con **Expression Builders**". Es otro patrón de Fowler y responde a esta pregunta: **¿dónde se programa la interfaz fluida?**

Una opción mala sería meter los métodos encadenables dentro de `Producto` (`Producto().nombre("x").precio(5)`). Eso ensucia el modelo con cosas de sintaxis y, además, tendríamos un `Producto` "a medio armar" sin nombre ni precio, que no se podría validar.

Un **Expression Builder** es una **clase aparte** que:
1. ofrece los métodos fluidos (`nombre()`, `precio()`, ...);
2. **va guardando** los valores mientras se encadenan;
3. al final **construye** el objeto real del modelo y lo valida.

```
 .producto(1).nombre("Arroz").precio(50)
       │           │              │
       ▼           ▼              ▼
 ProductoBuilder: _codigo=1, _nombre="Arroz", _precio=50   (todavía no existe ningún Producto)
       │
       │  cuando aparece el siguiente .producto() / .promocion() / .finalizar()
       ▼
 Producto(1, "Arroz", 50, None)   ← recién acá se crea y se valida
       │
       ▼
 supermercado.agregar_producto(...)
```

### Cómo está hecho en este repo ([DSL/Interno/DSLInterno.py](DSL/Interno/DSLInterno.py))

| Clase | Rol | Métodos |
|---|---|---|
| `DSLSupermercado` | Punto de entrada (primer nivel) | `producto()`, `promocion()`, `finalizar()` |
| `ProductoBuilder` | Arma un `Producto` | `nombre()`, `precio()`, `categoria()` |
| `PromocionBuilder` | Arma una `Promocion` | `nombre()`, `descuento()`, `cuando_producto()` |
| `CondicionBuilder` | Arma una `Condicion` | `cantidad_igual()`, `cantidad_mayor_igual()` |

Dos detalles que conviene entender para la defensa:

**a) ¿Cómo funciona `.precio(50).producto(2)` si `producto()` es del primer nivel?**
Los builders "hijos" también tienen `producto()`, `promocion()` y `finalizar()`, y lo único que hacen es **delegar** al padre (`return self._dsl.producto(codigo)`). Lo mismo pasa con `CondicionBuilder`: si después de `.cuando_producto(3)` llamás `.descuento(25)`, se lo pasa a la promoción. Así se puede escribir todo en una sola cadena.

**b) ¿Cuándo se guarda cada producto?**
Como los atributos pueden venir **en cualquier orden** (la letra lo exige), no se puede validar en `.nombre()`, porque tal vez el precio todavía no llegó. Por eso se guarda **cuando empieza el siguiente elemento** o en `finalizar()` (es el método `_guardar_actual`). Si el modelo tira un `ValueError`, se agrega a `dsl.errores` y la carga **sigue** (la letra pide no abortar).

---

## 6. Cómo funciona un DSL externo: lexer → parser → árbol → modelo

Leer un texto y "entenderlo" se hace en etapas. Este es el esquema que conviene tener en la cabeza:

```
 Texto del archivo
      │
      ▼
 ┌──────────┐   "COMPRA PRODUCTO 2 CANTIDAD 5 FIN"
 │  LEXER   │   corta el texto en TOKENS (palabras con tipo)
 └──────────┘
      │         COMPRA  PRODUCTO  INT(2)  CANTIDAD  INT(5)  FIN
      ▼
 ┌──────────┐   revisa que los tokens respeten la GRAMÁTICA
 │  PARSER  │   y arma un ÁRBOL de sintaxis
 └──────────┘
      │              compra
      │                └── linea
      │                     ├── 2
      │                     └── 5
      ▼
 ┌─────────────┐   recorre el árbol y llama al modelo semántico
 │ TRANSFORMER │   (en PLY esto lo hacen las funciones p_...)
 └─────────────┘
      │
      ▼
 Supermercado.registrar_compra([(2, 5)])
```

### 6.1 Tokens y lexer
- Un **token** es la unidad mínima con significado, como una "palabra" del lenguaje. Tiene **tipo** y **valor**: `INT` con valor `5`, o la palabra clave `PRODUCTO`.
- El **lexer** (o *analizador léxico*, *tokenizer*) lee el texto carácter por carácter y lo convierte en una lista de tokens. También **descarta** lo que no importa, como los espacios y los saltos de línea.

### 6.2 Gramática y reglas de producción
La **gramática** son las reglas que dicen qué secuencias de tokens son válidas. Cada regla se llama **regla de producción**. El informe PDF tiene que incluirlas.

Se escriben en notación **BNF** (*Backus-Naur Form*) o en su versión extendida, **EBNF**:

```
<inicio> ::= <compra> | <compra> <inicio>
<compra> ::= "COMPRA" <lineas> "FIN"
<lineas> ::= <linea> | <linea> <lineas>
<linea>  ::= "PRODUCTO" NUM | "PRODUCTO" NUM "CANTIDAD" NUM
```

Cómo se lee:
- `::=` significa "se define como".
- `|` significa "o".
- Lo que está entre `< >` es un **no terminal**: una regla que se sigue descomponiendo.
- Lo que está entre comillas, o `NUM`, es un **terminal**: un token concreto que ya no se descompone.
- Las reglas pueden ser **recursivas** (`<lineas>` usa `<lineas>`): así se expresa "una o más".

Para no tener que usar recursión, **EBNF** agrega estos símbolos:

| Símbolo | Significado | Ejemplo |
|---|---|---|
| `x?` o `[x]` | opcional (0 o 1) | `["CANTIDAD" NUM]` |
| `x*` | 0 o más | `atributo*` |
| `x+` | 1 o más | `linea+` |
| `( )` | agrupar | `("=" \| ">=")` |

La misma gramática en EBNF queda mucho más corta:

```
inicio : compra+
compra : "COMPRA" linea+ "FIN"
linea  : "PRODUCTO" NUM ["CANTIDAD" NUM]
```

### 6.3 Árbol de sintaxis
El parser no solo dice "sí, es válido": también arma un **árbol** que muestra la estructura. Para:

```
COMPRA
  PRODUCTO 2 CANTIDAD 5
  PRODUCTO 5
FIN
```

el árbol es:

```
inicio
└── compra
    ├── linea
    │   ├── 2
    │   └── 5
    └── linea
        ├── 5
        └── None      ← no se indicó CANTIDAD
```

Después, el **Transformer** recorre ese árbol y lo convierte en objetos del modelo.

---

## 7. Las herramientas: Lark y PLY

Las dos sirven para hacer el lexer y el parser sin programarlos a mano. La letra deja elegir, **salvo que el grupo sea de 3 personas**: en ese caso el anexo obliga a hacer **un DSL externo con Lark y el otro con PLY**.

### 7.1 Lark
La gramática se escribe **en un string**, en EBNF, y Lark arma todo solo.

```python
from lark import Lark, Transformer
from lark.exceptions import UnexpectedInput

gramatica = r"""
    inicio : compra+
    compra : "COMPRA" linea+ "FIN"
    linea  : "PRODUCTO" INT ["CANTIDAD" INT]

    %import common.INT
    %import common.WS
    %ignore WS
"""

class ComprasTransformer(Transformer):
    # Cada método se llama igual que una regla y recibe la lista de sus hijos.
    def linea(self, hijos):
        codigo, cantidad = hijos                 # cantidad es None si no vino CANTIDAD
        return int(codigo), int(cantidad) if cantidad is not None else 1

    def compra(self, hijos):
        return list(hijos)                       # lista de (codigo, cantidad)

    def inicio(self, hijos):
        return list(hijos)                       # lista de compras

parser = Lark(gramatica, start="inicio", parser="lalr")

texto = "COMPRA PRODUCTO 2 CANTIDAD 5 PRODUCTO 5 FIN"
try:
    arbol = parser.parse(texto)
    compras = ComprasTransformer().transform(arbol)
    print(compras)        # [[(2, 5), (5, 1)]]
except UnexpectedInput as error:
    print("Error de sintaxis:", error)
```

Cosas que hay que saber de Lark:
- Las palabras entre comillas en la gramática (`"COMPRA"`) son tokens **anónimos** y no aparecen en el árbol. Por eso `linea` recibe solo los dos números.
- Las MAYÚSCULAS (`INT`, `WS`) son **terminales** y las minúsculas (`linea`) son **reglas**.
- `%import common.INT` trae definiciones ya hechas: números enteros, decimales (`NUMBER`), strings entre comillas (`ESCAPED_STRING`), espacios (`WS`).
- `%ignore WS` le indica al lexer que descarte los espacios y los saltos de línea.
- `parser="lalr"` es el algoritmo más rápido y estricto. El otro, `"earley"`, acepta gramáticas más ambiguas pero es más lento.
- **Ojo con las comillas de la letra:** el PDF usa comillas tipográficas (`“Azúcar”`), no rectas (`"Azúcar"`). `ESCAPED_STRING` solo acepta las rectas. Para aceptar las dos hay que definir un terminal propio, por ejemplo `TEXTO: /"[^"]*"|“[^”]*”/`.

### 7.2 PLY (Python Lex-Yacc)
Es una versión en Python de **lex** y **yacc**, las herramientas clásicas de C. El lexer y el parser se definen **por separado**, con convenciones de nombres:
- `tokens = (...)` es la lista de todos los tipos de token;
- `t_ALGO` define el token `ALGO` con una expresión regular;
- `p_algo` define una regla de producción, y **la regla se escribe en el docstring** de la función.

```python
import ply.lex as lex
import ply.yacc as yacc

# ---------- LEXER ----------
tokens = ("COMPRA", "PRODUCTO", "CANTIDAD", "FIN", "NUMERO")

t_COMPRA   = r"COMPRA"
t_PRODUCTO = r"PRODUCTO"
t_CANTIDAD = r"CANTIDAD"
t_FIN      = r"FIN"
t_ignore   = " \t\r\n"          # caracteres que se descartan

def t_NUMERO(t):
    r"\d+"
    t.value = int(t.value)
    return t

def t_error(t):
    raise SyntaxError(f"Carácter inesperado: {t.value[0]!r}")

# ---------- PARSER ----------
def p_inicio(p):
    """inicio : compra
              | inicio compra"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_compra(p):
    "compra : COMPRA lineas FIN"
    p[0] = p[2]

def p_lineas(p):
    """lineas : linea
              | lineas linea"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_linea_con_cantidad(p):
    "linea : PRODUCTO NUMERO CANTIDAD NUMERO"
    p[0] = (p[2], p[4])

def p_linea_sin_cantidad(p):
    "linea : PRODUCTO NUMERO"
    p[0] = (p[2], 1)

def p_error(p):
    raise SyntaxError(f"Error de sintaxis cerca de {p.value!r}" if p else "Fin de archivo inesperado")

lexer = lex.lex()
parser = yacc.yacc()

print(parser.parse("COMPRA PRODUCTO 2 CANTIDAD 5 PRODUCTO 5 FIN", lexer=lexer))
# [[(2, 5), (5, 1)]]
```

Cómo se lee `p`: en `"compra : COMPRA lineas FIN"`, `p[1]` es `COMPRA`, `p[2]` es `lineas` y `p[3]` es `FIN`. A `p[0]` se le asigna el **resultado** de la regla.

PLY no tiene `+` ni `?`: las listas se arman con **recursión** (`lineas : lineas linea`) y lo opcional se resuelve con **dos reglas** (con y sin cantidad). Es, literalmente, BNF clásico.

PLY genera los archivos `parser.out` y `parsetab.py`. Son caché: conviene agregarlos al `.gitignore`.

### 7.3 Comparación (útil para justificar la elección en el informe)

| | Lark | PLY |
|---|---|---|
| Cómo se define la gramática | Un string en EBNF | Funciones con docstrings en BNF |
| Lexer | Lo arma solo | Se define a mano (`t_...`) |
| Listas y opcionales | `+`, `*`, `[ ]` | Recursión y reglas duplicadas |
| Resultado | Árbol + Transformer | Se arma el resultado en cada `p_...` |
| Algoritmos | LALR y Earley | Solo LALR |
| Mantenimiento | Activo | Ya no se mantiene (pero funciona) |
| Lo mejor | Gramática corta y legible | Control total y menos "magia" |

Para instalarlas: `pip install lark ply`.

---

## 8. Errores sintácticos vs. errores semánticos

La letra pide distinguirlos explícitamente.

| | Sintáctico | Semántico |
|---|---|---|
| ¿Qué es? | El texto **no respeta la gramática** | El texto es válido, pero **no tiene sentido** en el dominio |
| ¿Quién lo detecta? | El **parser** (Lark/PLY) | El **modelo semántico** |
| Ejemplo | `PRODUCTO CANTIDAD 5` (falta el código) | `AGREGAR PRODUCTO 1` cuando el 1 ya existe |
| Ejemplo | `COMPRA ... ` sin `FIN` | `ELIMINAR PRODUCTO 2` cuando el 2 está en una promoción |
| Ejemplo | `PRECIO abc` | `PRECIO 10.555` (más de 2 decimales)* |

\* Algunos casos pueden caer de un lado o del otro según cómo se escriba la gramática. Si la gramática solo acepta `INT` para los códigos, `PRODUCTO 2.5` es un error sintáctico. Si acepta `NUMBER` y el modelo controla que sea entero, pasa a ser semántico. Es una decisión de diseño que conviene explicar en el informe.

**Regla de la letra:** ante un error **semántico** el programa **no aborta**. Si en un archivo se agregan 3 productos y 2 fallan, el que está bien se agrega igual y se muestran los 2 errores. En la práctica:

```python
errores = []
for instruccion in instrucciones:
    try:
        instruccion.ejecutar(supermercado)
    except ValueError as error:
        errores.append(str(error))    # se anota y se sigue con la siguiente
```

Ante un error **sintáctico** el parser no puede seguir leyendo ese archivo, pero el **programa** tampoco tiene que cerrarse: se atrapa la excepción (`UnexpectedInput` en Lark, la que tire `p_error` en PLY), se muestra el mensaje y se vuelve al menú.

---

## 9. La lógica de las promociones

Esta es la parte de "algoritmo" del entregable. Reglas de la letra:

1. Una promoción se aplica solo si se cumplen **todas** sus condiciones.
2. Si una unidad podría entrar en varias promociones, se queda con la de **mayor porcentaje**.
3. Una unidad usada en una promoción **no se puede volver a usar** en otra.
4. Una promoción se puede aplicar **varias veces** si alcanzan las unidades.
5. El descuento se aplica **solo a los productos de la promoción**, no a toda la compra.

### Una forma simple de resolverlo (algoritmo "greedy" o goloso)

```
pendientes = {producto: cantidad comprada}
para cada promoción, de MAYOR a MENOR descuento:
    mientras se cumplan todas sus condiciones con lo que queda en "pendientes":
        aplicarla: esas unidades reciben el descuento
        restarlas de "pendientes"
lo que sobra en "pendientes" queda sin descuento
```

### Ejemplo de la letra (compra 2)
Promociones: **P1** = 1 Harina + 1 Levadura al 30% · **P2** = 2 Harina + 1 Azúcar al 20% · **P3** = 4 Harina al 10%.
Compra: 4 Harina, 1 Levadura, 1 Azúcar.

| Paso | Promoción | ¿Se cumple? | Pendientes después |
|---|---|---|---|
| inicio | | | H=4, L=1, A=1 |
| 1 | P1 (30%) | Sí: hay 1 H y 1 L | H=3, L=0, A=1 |
| 2 | P1 otra vez | No: L=0 | |
| 3 | P2 (20%) | Sí: hay 2 H y 1 A | H=1, L=0, A=0 |
| 4 | P2 otra vez | No: A=0 | |
| 5 | P3 (10%) | No: hace falta 4 H y queda 1 | |
| fin | | | 1 H sin descuento |

Resultado: **1 harina al 30%, 2 harinas al 20% y 1 harina sin descuento**, más la levadura al 30% y el azúcar al 20%. Coincide con la letra. Se puede verificar igual con las compras 1, 3, 4, 5 y 6.

Fijate que **un mismo producto termina en varias líneas** con descuentos distintos. Por eso cada línea de `Compra` tiene su propio "porcentaje de descuento".

### Importe de una línea
```
importe = precio × cantidad − (precio × cantidad × descuento / 100)
```
Ejemplo: 2 harinas a $30 con 20% → 60 − 12 = **$48**.

### Decisión pendiente: `>=`
Con "Harina **>=** 5" y una compra de 7 harinas, ¿el descuento va a las 7 o solo a 5? La letra no lo dice. Hay que elegir un criterio y **explicarlo en el informe**. Lo más natural es que vaya a las 7, porque "mayor o igual" sugiere "a partir de 5, todas".

---

## 10. Mapa del repositorio

| Archivo | Qué es | Concepto |
|---|---|---|
| [Objetos/Producto.py](Objetos/Producto.py) | Clase `Producto` con validaciones | Modelo semántico |
| [Objetos/Promocion.py](Objetos/Promocion.py) | Clase `Promocion` | Modelo semántico |
| [Objetos/Condicion.py](Objetos/Condicion.py) | Una condición de una promoción | Modelo semántico |
| [Objetos/Compra.py](Objetos/Compra.py) | Clase `Compra` (incompleta) | Modelo semántico |
| [Objetos/Supermercado.py](Objetos/Supermercado.py) | Contenedor y operaciones | Modelo semántico |
| [validaciones.py](validaciones.py) | Funciones auxiliares de validación | Modelo semántico |
| [DSL/Interno/DSLInterno.py](DSL/Interno/DSLInterno.py) | Builders fluidos | DSL interno: Fluent Interface + Expression Builder |
| [carga_inicial.py](carga_inicial.py) | La carga inicial usando el DSL interno | Uso del DSL interno |
| [DSL/Externo/DSLMantenimiento.py](DSL/Externo/DSLMantenimiento.py) | Gramática de mantenimiento (incompleta) | DSL externo + Lark |
| [DSL/Externo/DSLCompras.py](DSL/Externo/DSLCompras.py) | Gramática de compras (incompleta) | DSL externo + Lark |
| [aplicar_promociones.py](aplicar_promociones.py) | Algoritmo de promociones (vacío) | Lógica de dominio (sección 9) |
| *(falta)* `main.py` | Carga inicial + menú | Une todo |

---

## 11. Glosario rápido

- **DSL:** lenguaje pensado para un solo dominio.
- **DSL interno:** DSL escrito con la sintaxis de un lenguaje anfitrión (Python).
- **DSL externo:** DSL con sintaxis propia, que se lee con un parser.
- **Modelo semántico:** las clases del dominio (lo que *significan* los datos), independientes de la sintaxis.
- **Method chaining:** `a().b().c()`, posible porque cada método devuelve un objeto.
- **Fluent Interface:** estilo de API encadenada que se lee como lenguaje natural del dominio.
- **Expression Builder:** clase intermedia que ofrece la interfaz fluida, junta los datos y construye el objeto del modelo.
- **Token:** unidad mínima del texto (palabra clave, número, string).
- **Lexer:** convierte el texto en tokens.
- **Parser:** controla que los tokens respeten la gramática y arma el árbol.
- **Gramática:** conjunto de reglas de producción del lenguaje.
- **Regla de producción:** una regla del tipo `linea : "PRODUCTO" INT`.
- **Terminal / no terminal:** token concreto / regla que se sigue descomponiendo.
- **BNF / EBNF:** notaciones para escribir gramáticas (EBNF agrega `?`, `*`, `+`).
- **Árbol de sintaxis:** estructura jerárquica que arma el parser.
- **Transformer (Lark):** clase que recorre el árbol y lo convierte en objetos.
- **LALR:** algoritmo de parsing que usan PLY y Lark (con `parser="lalr"`).
- **Error sintáctico:** el texto no respeta la gramática (lo detecta el parser).
- **Error semántico:** el texto es válido pero no tiene sentido en el dominio (lo detecta el modelo).

---

## 12. Preguntas probables en la defensa

1. **¿Qué diferencia hay entre un DSL interno y uno externo?** Ver sección 2.
2. **¿Qué es el modelo semántico y por qué está separado de los DSL?** Para que los tres DSL compartan validaciones y lógica, y para poder cambiar uno sin tocar el resto.
3. **¿Dónde está el Expression Builder en su código?** En `ProductoBuilder`, `PromocionBuilder` y `CondicionBuilder`.
4. **¿Cómo lograron que los métodos vayan en cualquier orden?** El builder junta los valores y recién crea el objeto cuando empieza el siguiente elemento o en `finalizar()`.
5. **¿Cómo se cambiaría el DSL interno por otro?** Haciendo otra clase que llame a los mismos métodos de `Supermercado`. Ni el modelo ni el menú cambian.
6. **Muéstrenme las reglas de producción.** Hay que tener la gramática a mano.
7. **¿Por qué eligieron Lark (o PLY)?** Ver la tabla de la sección 7.3.
8. **Si un archivo tiene un error, ¿qué pasa?** Si es sintáctico, se informa y se vuelve al menú. Si es semántico, se informa y se siguen procesando las demás instrucciones.
9. **Explíquenme cómo se aplican las promociones en la compra X.** Hacer la tabla de la sección 9.
10. **¿Qué pasa con `>=`?** Explicar el criterio que eligieron.
