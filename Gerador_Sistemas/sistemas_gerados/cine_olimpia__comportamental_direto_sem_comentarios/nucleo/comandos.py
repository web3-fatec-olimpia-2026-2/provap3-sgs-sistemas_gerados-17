class Comando:
    def executar(self):
        raise NotImplementedError

    def desfazer(self):
        raise NotImplementedError


class AlterarCampo(Comando):
    def __init__(self, item, campo, valor):
        self.item = item
        self.campo = campo
        self.valor = valor
        self.anterior = None

    def executar(self):
        self.anterior = getattr(self.item, self.campo)
        setattr(self.item, self.campo, self.valor)

    def desfazer(self):
        setattr(self.item, self.campo, self.anterior)

    def __repr__(self):
        return f"AlterarCampo({self.campo}={self.valor!r})"


class Historico:
    def __init__(self):
        self._feitos = []
        self._desfeitos = []

    def executar(self, comando):
        comando.executar()
        self._feitos.append(comando)
        self._desfeitos.clear()

    def desfazer(self):
        if not self._feitos:
            return False
        comando = self._feitos.pop()
        comando.desfazer()
        self._desfeitos.append(comando)
        return True

    def refazer(self):
        if not self._desfeitos:
            return False
        comando = self._desfeitos.pop()
        comando.executar()
        self._feitos.append(comando)
        return True

    def acoes(self):
        return [repr(comando) for comando in self._feitos]
