"""Subsistemas PRONTOS do ex05. Cada um registra suas ações num log compartilhado (para os
testes conferirem a ORDEM). Não mexa aqui."""


class PagamentoRecusado(Exception):
    pass


class Estoque:
    def __init__(self, saldo, log):
        self._saldo = dict(saldo)          # {"cafe": 3, ...}
        self._log = log

    def tem(self, itens):
        self._log.append("estoque.tem")
        return all(self._saldo.get(produto, 0) >= qtd for produto, qtd in itens.items())

    def baixar(self, itens):
        self._log.append("estoque.baixar")
        for produto, qtd in itens.items():
            self._saldo[produto] -= qtd

    def saldo(self, produto):
        return self._saldo.get(produto, 0)


class Pagamentos:
    def __init__(self, log, recusar=False):
        self._log = log
        self._recusar = recusar

    def cobrar(self, cliente, valor):
        self._log.append("pagamentos.cobrar")
        if self._recusar:
            raise PagamentoRecusado("cartão recusado")
        return f"TX-{cliente}-{valor:.2f}"


class NotaFiscal:
    def __init__(self, log):
        self._log = log
        self.emitidas = []

    def emitir(self, cliente, valor):
        self._log.append("nota.emitir")
        numero = f"NF{len(self.emitidas) + 1:03d}"
        self.emitidas.append((numero, cliente, valor))
        return numero


class Email:
    def __init__(self, log):
        self._log = log
        self.enviados = []

    def enviar(self, cliente, mensagem):
        self._log.append("email.enviar")
        self.enviados.append((cliente, mensagem))


def finalizar_na_mao(cliente, itens, valor, estoque, pagamentos, nota, email):
    """O SMELL: todo cliente repete esta orquestração e conhece os 4 subsistemas."""
    if not estoque.tem(itens):
        return {"ok": False, "motivo": "sem estoque"}
    try:
        tx = pagamentos.cobrar(cliente, valor)
    except PagamentoRecusado:
        return {"ok": False, "motivo": "pagamento recusado"}
    estoque.baixar(itens)
    numero = nota.emitir(cliente, valor)
    email.enviar(cliente, f"Pedido confirmado - nota {numero}")
    return {"ok": True, "tx": tx, "nota": numero}
