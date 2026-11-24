"""
Cooperativa Citrícola — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

COMPONENTE       LoteCitrosBase(item)  → preco() / descricao()
DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
"""


class LoteCitrosBase:
    """COMPONENTE: expõe a LoteCitros pela interface preco()/descricao()."""

    def __init__(self, item):
        self._item = item

    def preco(self):
        return self._item.total

    def descricao(self):
        return f"LoteCitros de {self._item.cooperado} ({self._item.caixas} caixa(s))"


class Adicional:
    """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

    def __init__(self, componente):
        self._componente = componente  # pode ser LoteCitrosBase OU outro Adicional → por isso empilha

    def preco(self):
        return self._componente.preco()

    def descricao(self):
        return self._componente.descricao()


class ComFrete(Adicional):
    """Soma R$ 120.00 (frete até a indústria) ao que está DENTRO."""

    VALOR = 120.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + frete até a indústria"


class ComClassificacao(Adicional):
    """Soma R$ 60.00 (classificação por calibre) ao que está DENTRO."""

    VALOR = 60.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + classificação por calibre"


class ComCamaraFria(Adicional):
    """Soma R$ 90.00 (câmara fria) ao que está DENTRO."""

    VALOR = 90.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + câmara fria"


class ComBonusQualidade(Adicional):
    """MUDA comportamento: multiplica TUDO o que está dentro por 1.1 — aqui a ORDEM importa."""

    FATOR = 1.1

    def preco(self):
        return round(self._componente.preco() * self.FATOR, 2)

    def descricao(self):
        return self._componente.descricao() + " (+10% bônus de qualidade (brix))"
