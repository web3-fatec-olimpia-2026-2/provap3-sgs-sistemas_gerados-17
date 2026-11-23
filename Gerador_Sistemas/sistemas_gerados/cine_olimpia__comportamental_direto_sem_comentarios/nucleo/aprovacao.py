class Aprovador:
    nome = "aprovador"
    limite = 0.0

    def __init__(self):
        self.proximo = None

    def encadear(self, proximo):
        self.proximo = proximo
        return proximo

    def aprovar(self, item):
        if item.total <= self.limite:
            return self.nome
        if self.proximo is None:
            return "sem aprovador"
        return self.proximo.aprovar(item)


class Atendente(Aprovador):
    nome, limite = "atendente", 500.0


class Gerente(Aprovador):
    nome, limite = "gerente", 2000.0


class Diretoria(Aprovador):
    nome, limite = "diretoria", 10000.0


class Supervisor(Aprovador):
    nome, limite = "supervisor", 1000.0


def cadeia_padrao():
    inicio = Atendente()
    inicio.encadear(Gerente()).encadear(Diretoria())
    return inicio
