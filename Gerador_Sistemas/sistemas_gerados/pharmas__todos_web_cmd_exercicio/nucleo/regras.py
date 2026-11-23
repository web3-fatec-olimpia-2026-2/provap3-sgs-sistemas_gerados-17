"""
Pharmas — INTERPRETER (GoF · comportamental): regras escritas numa MINI-LINGUAGEM.

ANTES (nucleo/antes_regras.py): regra_antiga(item) com a condição fixa no código — toda mudança
("a partir de 3 unidade(s)") exige programar e publicar de novo.
DEPOIS (aqui):
  * cada pedaço da gramática é uma classe com interpretar(item): Comparacao, E, Ou;
  * ler_regra("quantidade >= 3 e total > 500") monta a ÁRVORE dessas classes;
  * a regra vira DADO (texto): dá para guardar no banco e trocar sem mexer no código.
Gramática:  regra := termo ("ou" termo)*      termo := comparacao ("e" comparacao)*
            comparacao := CAMPO OPERADOR NUMERO   (CAMPO: quantidade, valor_unitario ou total)
Quando NÃO usar: linguagem grande (use uma biblioteca de parsing) ou regra que nunca muda.
Nunca use eval() no lugar disto: eval executa QUALQUER código.
"""
import operator

OPERADORES = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt, "==": operator.eq}
CAMPOS = ("quantidade", "valor_unitario", "total")


class Comparacao:
    """Expressão TERMINAL: campo operador número (ex.: total > 500)."""

    def __init__(self, campo, simbolo, numero):
        if campo not in CAMPOS:
            raise ValueError(f"campo desconhecido: {campo}")
        if simbolo not in OPERADORES:
            raise ValueError(f"operador desconhecido: {simbolo}")
        self.campo, self.simbolo, self.numero = campo, simbolo, numero

    def interpretar(self, item):
        return OPERADORES[self.simbolo](getattr(item, self.campo), self.numero)


class E:
    """Expressão NÃO TERMINAL: verdadeira se TODAS as partes forem."""

    def __init__(self, *partes):
        self.partes = partes

    def interpretar(self, item):
        return all(parte.interpretar(item) for parte in self.partes)


class Ou:
    """Expressão NÃO TERMINAL: verdadeira se ALGUMA parte for."""

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
    """Transforma o TEXTO da regra na árvore de expressões ("e" vale antes de "ou")."""
    termos = []
    for termo in texto.strip().split(" ou "):
        termos.append(E(*[ler_comparacao(parte) for parte in termo.split(" e ")]))
    return Ou(*termos)
