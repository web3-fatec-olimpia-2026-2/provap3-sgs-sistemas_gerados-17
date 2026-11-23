from nucleo.integracao_base import PagamentoRecusado, ProcessadorPagamento


class PagueMaisAdapter(ProcessadorPagamento):
    MOEDA = "BRL"

    def __init__(self, gateway):
        self._gateway = gateway

    def processar(self, valor, token):
        payload = {"amount_cents": round(valor * 100), "card": token, "currency": self.MOEDA}
        resposta = self._gateway.charge(payload)
        if resposta["result"] == "approved":
            return resposta["tx"]
        raise PagamentoRecusado(resposta.get("reason", "recusado"))


class CheckoutService:
    def __init__(self, processador):
        self._processador = processador

    def pagar(self, item, token):
        valor = item.total
        try:
            return {"ok": True, "tx": self._processador.processar(valor, token), "valor": valor}
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}
