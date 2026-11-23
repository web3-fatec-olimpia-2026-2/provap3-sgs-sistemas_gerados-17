import copy


class Memento:
    def __init__(self, estado, rotulo):
        self._estado = copy.deepcopy(estado)
        self.rotulo = rotulo


class EditorIngresso:
    def __init__(self, item):
        self.item = item

    def alterar(self, campo, valor):
        setattr(self.item, campo, valor)

    def salvar(self, rotulo=""):
        return Memento(vars(self.item), rotulo)

    def restaurar(self, memento):
        self.item.__dict__.update(copy.deepcopy(memento._estado))


class HistoricoDeVersoes:
    def __init__(self):
        self._versoes = []

    def guardar(self, memento):
        self._versoes.append(memento)

    def ultima(self):
        return self._versoes.pop() if self._versoes else None

    def rotulos(self):
        return [memento.rotulo for memento in self._versoes]
