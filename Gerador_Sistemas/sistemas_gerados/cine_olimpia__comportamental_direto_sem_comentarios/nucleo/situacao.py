class TransicaoInvalida(Exception):
    pass


class Estado:
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


class SituacaoIngresso:
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
