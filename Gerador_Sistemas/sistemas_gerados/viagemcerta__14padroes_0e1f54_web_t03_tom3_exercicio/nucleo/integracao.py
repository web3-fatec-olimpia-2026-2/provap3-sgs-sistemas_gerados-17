"""
ViagemCerta — ADAPTER (Aula 08): fazer a peça de terceiro CABER na interface do sistema.

ALVO     ProcessadorPagamento.processar(valor, token)   (nucleo/integracao_base.py)
ADAPTADO GatewayPagaTur.charge({"amount_cents", "card", "currency"})   (terceiro)
ADAPTER  PagaTurAdapter — fala `processar` por fora e traduz para `charge` por dentro
Quando NÃO usar: se as duas pontas são nossas e parecidas, duck typing basta.
Adapter ≠ Facade: aqui é UMA peça e uma interface que JÁ existe.
"""
from nucleo.integracao_base import PagamentoRecusado, ProcessadorPagamento


class PagaTurAdapter(ProcessadorPagamento):
    """Veste o GatewayPagaTur com a interface ProcessadorPagamento (É-UM processador, TEM-UM gateway)."""

    MOEDA = "BRL"

    def __init__(self, gateway):
        self._gateway = gateway  # "_": detalhe interno; quem usa só chama processar()

    def processar(self, valor, token):
        # 1) dados de entrada: reais (float) → centavos (int); round evita 19.99*100 = 1998.999…
        payload = {"amount_cents": round(valor * 100), "card": token, "currency": self.MOEDA}
        # 2) a CHAMADA: processar → charge
        resposta = self._gateway.charge(payload)
        # 3) a SAÍDA: dict do terceiro → id (aprovado) ou exceção do NOSSO domínio (negado)
        if resposta["result"] == "approved":
            return resposta["tx"]
        raise PagamentoRecusado(resposta.get("reason", "recusado"))


class CheckoutService:
    """Serviço LIMPO: conhece só a interface ProcessadorPagamento. Zero 'if de gateway'."""

    def __init__(self, processador):
        self._processador = processador  # injeção: quem monta escolhe o gateway

    def pagar(self, item, token):
        valor = item.total
        try:
            return {"ok": True, "tx": self._processador.processar(valor, token), "valor": valor}
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}
