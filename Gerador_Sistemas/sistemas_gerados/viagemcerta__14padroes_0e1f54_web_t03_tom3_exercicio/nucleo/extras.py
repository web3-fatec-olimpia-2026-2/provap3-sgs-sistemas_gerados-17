"""
ViagemCerta — DECORATOR (Aula 10): somar opcionais empilhando embrulhos.

COMPONENTE       ViagcertBase(item)  → preco() / descricao()
DECORADOR BASE   Adicional          → guarda o embrulhado e DELEGA
DECORADORES      Com…               → chamam o de DENTRO e somam a SUA parte
Como a interface por fora é IGUAL à de dentro, um embrulho pode embrulhar outro: EMPILHA.
Quando NÃO usar: extras que só somam valor fixo → lista + sum() basta.
O @decorator do Python decora FUNÇÕES; este padrão decora OBJETOS.
"""


class ViagcertBase:
    """COMPONENTE: expõe a Viagcert pela interface preco()/descricao()."""

    def __init__(self, item):
        self._item = item

    def preco(self):
        return self._item.total

    def descricao(self):
        return f"Viagcert de {self._item.viajante} ({self._item.noites} noite(s))"


class Adicional:
    """DECORADOR BASE: mesma interface; guarda o objeto de dentro e, por padrão, só repassa."""

    def __init__(self, componente):
        self._componente = componente  # pode ser ViagcertBase OU outro Adicional → por isso empilha

    def preco(self):
        return self._componente.preco()

    def descricao(self):
        return self._componente.descricao()


class ComSeguroViagem(Adicional):
    """Soma R$ 90.00 (seguro viagem) ao que está DENTRO."""

    VALOR = 90.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + seguro viagem"


class ComTranslado(Adicional):
    """Soma R$ 120.00 (translado) ao que está DENTRO."""

    VALOR = 120.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + translado"


class ComPasseioGuiado(Adicional):
    """Soma R$ 150.00 (passeio guiado) ao que está DENTRO."""

    VALOR = 150.0

    def preco(self):
        return round(self._componente.preco() + self.VALOR, 2)  # de dentro + a minha parte

    def descricao(self):
        return self._componente.descricao() + " + passeio guiado"


class ComAltaTemporada(Adicional):
    """MUDA comportamento: multiplica TUDO o que está dentro por 1.25 — aqui a ORDEM importa."""

    FATOR = 1.25

    def preco(self):
        return round(self._componente.preco() * self.FATOR, 2)

    def descricao(self):
        return self._componente.descricao() + " (+25% alta temporada)"
