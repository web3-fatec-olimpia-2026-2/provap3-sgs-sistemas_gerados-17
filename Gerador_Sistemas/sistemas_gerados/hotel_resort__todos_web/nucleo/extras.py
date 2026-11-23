"""
Hotel Resort — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

COMPONENTE       ReservaBase(item)  → preco() / descricao()
DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
"""


class ReservaBase:
    """COMPONENTE: expõe a Reserva pela interface preco()/descricao()."""

    def __init__(self, item):
        self._item = item

    def preco(self):
        return self._item.total

    def descricao(self):
        return f"Reserva de {self._item.hospede} ({self._item.diarias} diária(s))"


class Adicional:
    """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

    def __init__(self, componente):
        self._componente = componente  # pode ser ReservaBase OU outro Adicional → por isso empilha

    def preco(self):
        return self._componente.preco()

    def descricao(self):
        return self._componente.descricao()


class ComCafeDaManha(Adicional):
    """Soma R$ 40.00 (café da manhã) ao que está DENTRO."""

    VALOR = 40.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + café da manhã"


class ComTransfer(Adicional):
    """Soma R$ 80.00 (transfer) ao que está DENTRO."""

    VALOR = 80.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + transfer"


class ComLateCheckout(Adicional):
    """Soma R$ 60.00 (late checkout) ao que está DENTRO."""

    VALOR = 60.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + late checkout"


class ComDescontoFidelidade(Adicional):
    """MUDA comportamento: multiplica TUDO o que está dentro por 0.9 — aqui a ORDEM importa."""

    FATOR = 0.9

    def preco(self):
        return round(self._componente.preco() * self.FATOR, 2)

    def descricao(self):
        return self._componente.descricao() + " (-10% fidelidade)"
