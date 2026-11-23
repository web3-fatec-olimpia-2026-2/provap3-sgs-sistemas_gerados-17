"""ANTES — o smell do Adapter: o serviço conhece os dois mundos e decide no if."""
from nucleo.integracao_base import PagamentoRecusado


class CheckoutAntigo:
    def __init__(self, interno, gateway, usa_gateway):
        self.interno, self.gateway, self.usa_gateway = interno, gateway, usa_gateway

    def pagar(self, item, token):
        valor = item.total
        if self.usa_gateway:  # ← detalhe do terceiro vazando para a regra
            resp = self.gateway.charge({"amount_cents": round(valor * 100), "card": token, "currency": "BRL"})
            if resp["result"] == "approved":
                return {"ok": True, "tx": resp["tx"], "valor": valor}
            return {"ok": False, "motivo": resp["reason"]}
        try:
            return {"ok": True, "tx": self.interno.processar(valor, token), "valor": valor}
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}
