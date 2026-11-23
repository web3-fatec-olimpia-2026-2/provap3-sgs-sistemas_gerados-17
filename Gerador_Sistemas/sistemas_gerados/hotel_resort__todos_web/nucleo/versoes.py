"""
Hotel Resort — MEMENTO (GoF · comportamental): guardar e restaurar o ESTADO sem expor o interior.

ANTES (nucleo/antes_versoes.py): para "voltar atrás", quem usava copiava os campos internos (_x) na
mão — dependia do interior da Reserva e esquecia campos novos.
DEPOIS (aqui):
  * EditorReserva (o ORIGINADOR) cria um Memento com o próprio estado e sabe restaurar a partir dele;
  * Memento é uma "caixa fechada": guarda uma CÓPIA do estado; só o originador abre;
  * HistoricoDeVersoes (o ZELADOR) só empilha mementos — nunca olha dentro.
Memento × Command: o Command desfaz UMA ação (sabe o inverso dela); o Memento volta o ESTADO inteiro.
Quando NÃO usar: estado enorme e muitas versões (memória) — guarde só as diferenças ou use Command.
"""
import copy


class Memento:
    """Caixa fechada com uma cópia do estado (o rótulo é público; o conteúdo, não)."""

    def __init__(self, estado, rotulo):
        self._estado = copy.deepcopy(estado)
        self.rotulo = rotulo


class EditorReserva:
    """ORIGINADOR: edita a Reserva e sabe salvar/restaurar o próprio estado."""

    def __init__(self, item):
        self.item = item

    def alterar(self, campo, valor):
        setattr(self.item, campo, valor)  # continua passando pelo setter (validado)

    def salvar(self, rotulo=""):
        return Memento(vars(self.item), rotulo)

    def restaurar(self, memento):
        # O estado guardado já foi válido: volta inteiro (cópia, para o memento seguir intacto).
        self.item.__dict__.update(copy.deepcopy(memento._estado))


class HistoricoDeVersoes:
    """ZELADOR: guarda os mementos em ordem; não sabe o que tem dentro deles."""

    def __init__(self):
        self._versoes = []

    def guardar(self, memento):
        self._versoes.append(memento)

    def ultima(self):
        return self._versoes.pop() if self._versoes else None

    def rotulos(self):
        return [memento.rotulo for memento in self._versoes]
