"""
Hotel Resort — OBSERVER (GoF · comportamental): quem se INSCREVE é avisado quando algo muda.

ANTES (nucleo/antes_eventos.py): alterar_antigo(...) chamava, um por um, o painel e o log — cada
interessado novo obrigava a editar a função (e ela conhecia todos).
DEPOIS (aqui):
  * ReservaObservavel (o SUJEITO) guarda a lista de observadores e avisa todos: notificar(evento);
  * cada observador implementa atualizar(evento) e decide o que fazer;
  * interessado novo = inscrever(obj) — o sujeito não muda.
Quando NÃO usar: um único interessado, fixo — chame-o direto. Cadeias de observadores escondem o fluxo.
"""


class ReservaObservavel:
    """SUJEITO: embrulha a Reserva e avisa os inscritos a cada mudança."""

    def __init__(self, item):
        self.item = item
        self._observadores = []

    def inscrever(self, observador):
        self._observadores.append(observador)

    def cancelar(self, observador):
        self._observadores.remove(observador)

    def alterar(self, campo, valor):
        anterior = self.item.total
        setattr(self.item, campo, valor)  # o setter valida ANTES de avisar alguém
        self.notificar({"campo": campo, "valor": valor, "total_anterior": anterior, "total": self.item.total})

    def notificar(self, evento):
        for observador in list(self._observadores):  # cópia: alguém pode se cancelar no meio
            observador.atualizar(evento)


class PainelObservador:
    """Mostra sempre o total mais recente."""

    def __init__(self):
        self.total = None

    def atualizar(self, evento):
        self.total = evento["total"]


class LogObservador:
    """Registra cada mudança em texto."""

    def __init__(self):
        self.linhas = []

    def atualizar(self, evento):
        self.linhas.append(f"{evento['campo']} -> {evento['valor']} (total R$ {evento['total']:.2f})")


class AlertaObservador:
    """Observador NOVO: alerta quando o total passa do limite (o sujeito não mudou)."""

    def __init__(self, limite):
        self.limite = limite
        self.alertas = []

    def atualizar(self, evento):
        if evento["total"] > self.limite >= evento["total_anterior"]:
            self.alertas.append(f"total passou de R$ {self.limite:.2f}")
