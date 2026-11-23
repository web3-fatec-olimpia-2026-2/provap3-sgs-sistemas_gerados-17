"""ex04 — Adapter. SEU ARQUIVO: construa o PagaFacilAdapter."""
from base_pagamento import (Checkout, CheckoutAntigo, GatewayPagaFacil,  # noqa: F401
                            PagamentoRecusado, ProcessadorFake, ProcessadorPagamento)


class PagaFacilAdapter(ProcessadorPagamento):
    def __init__(self, gateway):
        raise NotImplementedError   # TODO: guardar o gateway

    def processar(self, valor, token_cartao):
        raise NotImplementedError   # TODO: reais→centavos, chamar charge, traduzir a resposta
