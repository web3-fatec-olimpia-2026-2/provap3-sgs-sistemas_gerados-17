import operator

OPERADORES = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}
CAMPOS = ("quantidade", "preco", "total")


class Comparacao:
    def __init__(self, campo, simbolo, numero):
        if campo not in CAMPOS:
            raise ValueError(f"campo desconhecido: {campo}")
        if simbolo not in OPERADORES:
            raise ValueError(f"operador desconhecido: {simbolo}")
        self.campo, self.simbolo, self.numero = campo, simbolo, numero

    def interpretar(self, item):
        return OPERADORES[self.simbolo](getattr(item, self.campo), self.numero)


class E:
    def __init__(self, *partes):
        self.partes = partes

    def interpretar(self, item):
        return all(parte.interpretar(item) for parte in self.partes)


class Ou:
    def __init__(self, *partes):
        self.partes = partes

    def interpretar(self, item):
        return any(parte.interpretar(item) for parte in self.partes)


def ler_comparacao(texto):
    partes = texto.split()
    if len(partes) != 3:
        raise ValueError(f"comparação mal escrita: {texto!r} (use: campo operador número)")
    campo, simbolo, numero = partes
    try:
        valor = float(numero)
    except ValueError:
        raise ValueError(f"número inválido: {numero!r}") from None
    return Comparacao(campo, simbolo, valor)


def ler_regra(texto):
    termos = []
    for termo in texto.strip().split(" ou "):
        termos.append(E(*[ler_comparacao(parte) for parte in termo.split(" e ")]))
    return Ou(*termos)
