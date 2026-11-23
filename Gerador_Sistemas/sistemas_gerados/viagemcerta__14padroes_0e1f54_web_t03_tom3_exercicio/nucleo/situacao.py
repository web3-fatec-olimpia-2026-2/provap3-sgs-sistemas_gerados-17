"""
ViagemCerta — STATE (GoF · comportamental): o comportamento muda conforme o ESTADO do objeto.

ANTES (nucleo/antes_situacao.py): cada método tinha um if/elif sobre self.status ("aberto",
"confirmado"...) — a mesma escada repetida em confirmar, concluir e cancelar.
DEPOIS (aqui):
  * cada estado é uma classe (Aberto, Confirmado, Concluido, Cancelado) que sabe as SUAS transições;
  * SituacaoViagcert (o CONTEXTO) guarda o estado atual e DELEGA: self.estado.confirmar(self);
  * transição proibida levanta TransicaoInvalida; estado novo = classe nova.
State × Strategy: mesma estrutura (contexto delega a um objeto); no State o PRÓPRIO estado troca o
objeto do contexto (Aberto → Confirmado); no Strategy quem escolhe é o cliente.
Quando NÃO usar: 2 estados e uma regra (um booleano basta).
"""


class TransicaoInvalida(Exception):
    """Ação que não faz sentido no estado atual."""


class Estado:
    """Estado BASE: por padrão, nenhuma ação é permitida."""

    nome = "?"

    def confirmar(self, contexto):
        raise TransicaoInvalida(f"não dá para confirmar: está {self.nome}")

    def concluir(self, contexto):
        raise TransicaoInvalida(f"não dá para concluir: está {self.nome}")

    def cancelar(self, contexto):
        raise TransicaoInvalida(f"não dá para cancelar: está {self.nome}")


class Aberto(Estado):
    nome = "aberto"

    def confirmar(self, contexto):
        contexto.estado = Confirmado()

    def cancelar(self, contexto):
        contexto.estado = Cancelado()


class Confirmado(Estado):
    nome = "confirmado"

    def concluir(self, contexto):
        contexto.estado = Concluido()

    def cancelar(self, contexto):
        contexto.estado = Cancelado()


class Concluido(Estado):
    nome = "concluido"


class Cancelado(Estado):
    nome = "cancelado"


class SituacaoViagcert:
    """CONTEXTO: a Viagcert + o estado atual. As ações são DELEGADAS ao estado."""

    def __init__(self, item):
        self.item = item
        self.estado = Aberto()

    @property
    def status(self):
        return self.estado.nome

    def confirmar(self):
        self.estado.confirmar(self)

    def concluir(self):
        self.estado.concluir(self)

    def cancelar(self):
        self.estado.cancelar(self)
