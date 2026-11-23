class PedidoBase:
    def __init__(self, item):
        self._item = item

    def preco(self):
        return self._item.total

    def descricao(self):
        return f"Pedido de {self._item.cliente} ({self._item.quantidade} unidade(s))"


class Adicional:
    def __init__(self, componente):
        self._componente = componente

    def preco(self):
        return self._componente.preco()

    def descricao(self):
        return self._componente.descricao()


class ComEmbrulho(Adicional):
    VALOR = 15.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)

    def descricao(self):
        return self._componente.descricao() + " + embrulho para presente"


class ComCartao(Adicional):
    VALOR = 5.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)

    def descricao(self):
        return self._componente.descricao() + " + cartão"


class ComEntregaExpressa(Adicional):
    VALOR = 25.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)

    def descricao(self):
        return self._componente.descricao() + " + entrega expressa"


class ComCupom10(Adicional):
    FATOR = 0.9

    def preco(self):
        return round(self._componente.preco() * self.FATOR, 2)

    def descricao(self):
        return self._componente.descricao() + " (-10% cupom)"
