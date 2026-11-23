"""ex06 — Decorator. SEU ARQUIVO (PedidoBase e preco_com_flags estão prontos)."""


class PedidoBase:
    def __init__(self, valor):
        self.valor = valor

    def preco(self):
        return self.valor

    def descricao(self):
        return f"Pedido R$ {self.valor:.2f}"


def preco_com_flags(valor, embrulho=False, cartao=False, expressa=False):
    """O SMELL: cada extra = mais um parâmetro e mais um if."""
    total = valor
    if embrulho:
        total += 15
    if cartao:
        total += 5
    if expressa:
        total += 25
    return total


class Opcional:
    def __init__(self, pedido):
        raise NotImplementedError   # TODO

    def preco(self):
        raise NotImplementedError   # TODO

    def descricao(self):
        raise NotImplementedError   # TODO


class ComEmbrulho(Opcional):
    pass                            # TODO


class ComCartao(Opcional):
    pass                            # TODO


class ComEntregaExpressa(Opcional):
    pass                            # TODO


class ComCupom10(Opcional):
    pass                            # TODO
