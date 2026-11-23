"""
Peças PRONTAS do Adapter (não mexer): a interface do NOSSO sistema e o gateway de TERCEIRO.
"""


class PagamentoRecusado(Exception):
    """Erro de domínio: o sistema inteiro trata recusa com esta exceção."""


class ProcessadorPagamento:
    """ALVO: a interface que o nosso sistema espera."""

    def processar(self, valor, token):
        raise NotImplementedError


class ProcessadorInterno(ProcessadorPagamento):
    """Implementação NOSSA (já fala a língua certa — não precisa de adapter)."""

    def __init__(self):
        self._seq = 0

    def processar(self, valor, token):
        if token == "tok_recusado":
            raise PagamentoRecusado("cartão recusado")
        self._seq += 1
        return f"INT-{self._seq:04d}"


class GatewayCobraJa:
    """ADAPTADO: biblioteca de TERCEIRO — não controlamos esta assinatura."""

    def __init__(self):
        self.recebidos = []
        self._seq = 0

    def charge(self, payload):
        self.recebidos.append(dict(payload))
        if payload["card"] == "tok_recusado":
            return {"result": "denied", "reason": "cartão recusado"}
        if payload["amount_cents"] <= 0:
            return {"result": "denied", "reason": "valor inválido"}
        self._seq += 1
        return {"result": "approved", "tx": f"CJ-{self._seq:04d}"}
