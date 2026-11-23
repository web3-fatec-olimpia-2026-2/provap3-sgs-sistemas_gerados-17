"""ex06 — GABARITO comentado: Decorator nos opcionais do pedido."""


class PedidoBase:
    """COMPONENTE: o objeto que será embrulhado."""

    def __init__(self, valor):
        self.valor = valor

    def preco(self):
        return self.valor

    def descricao(self):
        return f"Pedido R$ {self.valor:.2f}"


def preco_com_flags(valor, embrulho=False, cartao=False, expressa=False):
    total = valor
    if embrulho:
        total += 15
    if cartao:
        total += 5
    if expressa:
        total += 25
    return total


class Opcional:
    """DECORADOR BASE: mesma interface do componente; por padrão só repassa."""

    def __init__(self, pedido):
        self._pedido = pedido        # pode ser PedidoBase ou outro Opcional → por isso empilha

    def preco(self):
        return self._pedido.preco()

    def descricao(self):
        return self._pedido.descricao()


class _SomaFixa(Opcional):
    """Atalho para os extras que só somam um valor fixo (evita repetir 3x o mesmo código).
    Subclasses definem VALOR e TEXTO."""

    VALOR = 0
    TEXTO = ""

    def preco(self):
        return self._pedido.preco() + self.VALOR          # o de dentro + a minha parte

    def descricao(self):
        return self._pedido.descricao() + self.TEXTO


class ComEmbrulho(_SomaFixa):
    VALOR, TEXTO = 15, " + embrulho"


class ComCartao(_SomaFixa):
    VALOR, TEXTO = 5, " + cartao"


class ComEntregaExpressa(_SomaFixa):
    VALOR, TEXTO = 25, " + entrega expressa"


class ComCupom10(Opcional):
    """Este NÃO soma valor fixo: MUDA o comportamento (multiplica tudo o que está dentro).
    É o caso em que o Decorator mais se justifica — e em que a ORDEM passa a importar."""

    def preco(self):
        return round(self._pedido.preco() * 0.9, 2)

    def descricao(self):
        return self._pedido.descricao() + " (-10% cupom)"


# Para explicar na P3:
# - Embrulho/cartão/expressa só SOMAM → soma é comutativa → a ordem não muda o preço.
#   O cupom MULTIPLICA o que está dentro → aplicado por fora desconta os extras; por dentro, não.
# - Dois cartões = ComCartao(ComCartao(...)); com flag booleana só existe "tem ou não tem".
# - Se TODOS os extras fossem só "+ valor fixo", uma lista de extras + sum() resolveria e o
#   Decorator seria cerimônia (delimitação em Python). O cupom é o que justifica o padrão aqui.
# - Não confundir com o @decorator do Python (que decora funções).
