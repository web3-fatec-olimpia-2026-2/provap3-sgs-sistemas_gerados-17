class IngressoObservavel:
    def __init__(self, item):
        self.item = item
        self._observadores = []

    def inscrever(self, observador):
        self._observadores.append(observador)

    def cancelar(self, observador):
        self._observadores.remove(observador)

    def alterar(self, campo, valor):
        anterior = self.item.total
        setattr(self.item, campo, valor)
        self.notificar({"campo": campo, "valor": valor, "total_anterior": anterior, "total": self.item.total})

    def notificar(self, evento):
        for observador in list(self._observadores):
            observador.atualizar(evento)


class PainelObservador:
    def __init__(self):
        self.total = None

    def atualizar(self, evento):
        self.total = evento["total"]


class LogObservador:
    def __init__(self):
        self.linhas = []

    def atualizar(self, evento):
        self.linhas.append(f"{evento['campo']} -> {evento['valor']} (total R$ {evento['total']:.2f})")


class AlertaObservador:
    def __init__(self, limite):
        self.limite = limite
        self.alertas = []

    def atualizar(self, evento):
        if evento["total"] > self.limite >= evento["total_anterior"]:
            self.alertas.append(f"total passou de R$ {self.limite:.2f}")
