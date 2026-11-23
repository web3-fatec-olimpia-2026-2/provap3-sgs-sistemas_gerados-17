class PagamentoRecusado(Exception):
    pass


class ProcessadorPagamento:
    def processar(self, valor, token):
        raise NotImplementedError


class ProcessadorInterno(ProcessadorPagamento):
    def __init__(self):
        self._seq = 0

    def processar(self, valor, token):
        if token == "tok_recusado":
            raise PagamentoRecusado("cartão recusado")
        self._seq += 1
        return f"INT-{self._seq:04d}"


class GatewayPagueMais:
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
        return {"result": "approved", "tx": f"PM-{self._seq:04d}"}
