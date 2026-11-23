"""Peças PRONTAS do ex04 (usadas pelo exercicio.py e pelo gabarito.py). Não mexa aqui."""


class PagamentoRecusado(Exception):
    """Erro de domínio: o sistema inteiro trata recusa com esta exceção."""


class ProcessadorPagamento:
    """ALVO: a interface que o NOSSO sistema espera."""

    def processar(self, valor: float, token_cartao: str) -> str:
        raise NotImplementedError


class ProcessadorFake(ProcessadorPagamento):
    """Implementação nossa, usada em testes: recusa o token 'tok_recusado'."""

    def __init__(self):
        self._seq = 0

    def processar(self, valor, token_cartao):
        if token_cartao == "tok_recusado":
            raise PagamentoRecusado("cartão recusado")
        self._seq += 1
        return f"FAKE-{self._seq:04d}"


class GatewayPagaFacil:
    """ADAPTADO: biblioteca de TERCEIRO (assinatura que não controlamos)."""

    def __init__(self):
        self.recebidos = []
        self._seq = 0

    def charge(self, payload: dict) -> dict:
        self.recebidos.append(dict(payload))
        if payload["card"] == "tok_recusado":
            return {"result": "denied", "reason": "cartão recusado"}
        if payload["amount_cents"] <= 0:
            return {"result": "denied", "reason": "valor inválido"}
        self._seq += 1
        return {"result": "approved", "tx": f"PF-{self._seq:04d}"}


class Checkout:
    """Serviço LIMPO: conhece só a interface ProcessadorPagamento. Zero 'if de gateway'."""

    def __init__(self, processador: ProcessadorPagamento):
        self._processador = processador

    def pagar(self, valor, token_cartao):
        try:
            return {"ok": True, "tx": self._processador.processar(valor, token_cartao)}
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}


class CheckoutAntigo:
    """O SMELL: o serviço conhece os dois mundos e decide no if."""

    def __init__(self, fake, gateway, usa_pagafacil):
        self.fake, self.gateway, self.usa_pagafacil = fake, gateway, usa_pagafacil

    def pagar(self, valor, token):
        if self.usa_pagafacil:
            resp = self.gateway.charge({"amount_cents": round(valor * 100), "card": token, "currency": "BRL"})
            if resp["result"] == "approved":
                return {"ok": True, "tx": resp["tx"]}
            return {"ok": False, "motivo": resp["reason"]}
        try:
            return {"ok": True, "tx": self.fake.processar(valor, token)}
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}
