"""
Loja Virtual — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

COMPONENTE       PedidoBase(item)  → preco() / descricao()
DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
"""


class PedidoBase:
    """COMPONENTE: expõe a Pedido pela interface preco()/descricao()."""

    def __init__(self, item):
        self._item = item

    def preco(self):
        return self._item.total

    def descricao(self):
        return f"Pedido de {self._item.cliente} ({self._item.quantidade} unidade(s))"


class Adicional:
    """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

    def __init__(self, componente):
        self._componente = componente  # pode ser PedidoBase OU outro Adicional → por isso empilha

    def preco(self):
        return self._componente.preco()

    def descricao(self):
        return self._componente.descricao()


class ComEmbrulho(Adicional):
    """Soma R$ 15.00 (embrulho para presente) ao que está DENTRO."""

    VALOR = 15.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + embrulho para presente"


class ComCartao(Adicional):
    """Soma R$ 5.00 (cartão) ao que está DENTRO."""

    VALOR = 5.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + cartão"


class ComEntregaExpressa(Adicional):
    """Soma R$ 25.00 (entrega expressa) ao que está DENTRO."""

    VALOR = 25.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + entrega expressa"


class ComCupom10(Adicional):
    """MUDA comportamento: multiplica TUDO o que está dentro por 0.9 — aqui a ORDEM importa."""

    FATOR = 0.9

    def preco(self):
        return round(self._componente.preco() * self.FATOR, 2)

    def descricao(self):
        return self._componente.descricao() + " (-10% cupom)"
