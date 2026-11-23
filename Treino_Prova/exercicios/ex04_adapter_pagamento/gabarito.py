"""ex04 — GABARITO comentado: Adapter para o gateway PagaFácil."""
from base_pagamento import (Checkout, CheckoutAntigo, GatewayPagaFacil,  # noqa: F401
                            PagamentoRecusado, ProcessadorFake, ProcessadorPagamento)


class PagaFacilAdapter(ProcessadorPagamento):
    """Veste o GatewayPagaFacil com a interface ProcessadorPagamento.

    Por FORA:  processar(valor_em_reais, token) -> id | PagamentoRecusado   (a língua do sistema)
    Por DENTRO: charge({"amount_cents", "card", "currency"}) -> {"result", ...} (a língua do terceiro)
    """

    MOEDA = "BRL"

    def __init__(self, gateway):
        self._gateway = gateway          # composição: o adapter TEM-UM gateway

    def processar(self, valor, token_cartao):
        # 1) traduz os DADOS de entrada: reais (float) → centavos (int).
        #    round() evita o erro de ponto flutuante (19.99 * 100 = 1998.9999...).
        payload = {"amount_cents": round(valor * 100), "card": token_cartao, "currency": self.MOEDA}
        # 2) traduz a CHAMADA: processar → charge
        resposta = self._gateway.charge(payload)
        # 3) traduz a SAÍDA: dict do terceiro → id (sucesso) ou exceção de domínio (recusa)
        if resposta["result"] == "approved":
            return resposta["tx"]
        raise PagamentoRecusado(resposta.get("reason", "recusado"))


# Para explicar na P3:
# - Adapter (não Facade) porque é UMA peça de terceiro com interface diferente, e o objetivo é
#   ela CABER numa interface que já existe; não estou escondendo vários subsistemas.
# - Ganho: o Checkout não tem "if usa_pagafacil"; trocar de gateway = injetar outro processador.
# - Se o PagaFácil fosse nosso, mudaríamos o próprio código para ter processar() (duck typing);
#   o Adapter se justifica quando NÃO controlamos a assinatura.
