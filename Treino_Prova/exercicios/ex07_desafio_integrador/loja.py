"""
ex07 — Desafio integrador: o checkout do "Empório" (código PRONTO — é o objeto do simulado).

Leia este arquivo como se fosse o código da sua equipe na P3. NÃO edite: as extensões pedidas
no simulado vão em `extensoes.py`.
"""


# ===========================================================================
# 1) FRETE
# ===========================================================================
class FretePAC:
    def calcular(self, peso_kg):
        return 10 + 2 * peso_kg


class FreteRetirada:
    def calcular(self, peso_kg):
        return 0


# ===========================================================================
# 2) CARRINHO E OPCIONAIS
# ===========================================================================
class Carrinho:
    def __init__(self, itens):
        self.itens = list(itens)                 # [(nome, preco), ...]

    def preco(self):
        return sum(preco for _, preco in self.itens)

    def descricao(self):
        return f"Carrinho ({len(self.itens)} itens)"


class Opcional:
    def __init__(self, pedido):
        self._pedido = pedido

    def preco(self):
        return self._pedido.preco()

    def descricao(self):
        return self._pedido.descricao()


class ComEmbrulho(Opcional):
    def preco(self):
        return self._pedido.preco() + 15

    def descricao(self):
        return self._pedido.descricao() + " + embrulho"


class ComCupom10(Opcional):
    def preco(self):
        return round(self._pedido.preco() * 0.9, 2)

    def descricao(self):
        return self._pedido.descricao() + " (-10%)"


# ===========================================================================
# 3) PAGAMENTO
# ===========================================================================
class PagamentoRecusado(Exception):
    pass


class GatewayPagaFacil:                          # biblioteca de terceiro
    def __init__(self):
        self._seq = 0

    def charge(self, payload):
        if payload["card"] == "tok_recusado":
            return {"result": "denied", "reason": "cartão recusado"}
        self._seq += 1
        return {"result": "approved", "tx": f"PF-{self._seq:04d}"}


class PagaFacilAdapter:
    def __init__(self, gateway):
        self._gateway = gateway

    def processar(self, valor, token):
        resp = self._gateway.charge({"amount_cents": round(valor * 100), "card": token})
        if resp["result"] != "approved":
            raise PagamentoRecusado(resp["reason"])
        return resp["tx"]


# ===========================================================================
# 4) REGRAS DO PEDIDO
# ===========================================================================
class PedidoService:
    FRETE_GRATIS_A_PARTIR_DE = 200

    def total(self, carrinho, frete, peso_kg):
        subtotal = carrinho.preco()
        if subtotal >= self.FRETE_GRATIS_A_PARTIR_DE:
            valor_frete = 0
        else:
            valor_frete = frete.calcular(peso_kg)
        return round(subtotal + valor_frete, 2), valor_frete


# ===========================================================================
# 5) CHECKOUT
# ===========================================================================
class EmailFake:
    def __init__(self):
        self.enviados = []

    def enviar(self, cliente, msg):
        self.enviados.append((cliente, msg))


class CheckoutFacade:
    def __init__(self, service, processador, email):
        self._service, self._processador, self._email = service, processador, email

    def finalizar(self, cliente, carrinho, frete, peso_kg, token):
        total, valor_frete = self._service.total(carrinho, frete, peso_kg)
        try:
            tx = self._processador.processar(total, token)
        except PagamentoRecusado as erro:
            return {"ok": False, "motivo": str(erro)}
        self._email.enviar(cliente, f"Pedido pago: R$ {total:.2f}")
        return {"ok": True, "tx": tx, "total": total, "frete": valor_frete}


# ===========================================================================
# 6) TELA
# ===========================================================================
class ResumoPedidoVM:
    def __init__(self, resultado):
        if resultado["ok"]:
            self.titulo = "Pedido confirmado"
            self.selo = "verde"
            self.valor_formatado = f"R$ {resultado['total']:.2f}"
            self.frete_label = ("Frete grátis" if resultado["frete"] == 0
                                else f"Frete R$ {resultado['frete']:.2f}")
        else:
            self.titulo = "Pagamento não realizado"
            self.selo = "vermelho"
            self.valor_formatado = "-"
            self.frete_label = ""


def montar_checkout():
    """Monta o checkout com as peças reais."""
    return CheckoutFacade(PedidoService(), PagaFacilAdapter(GatewayPagaFacil()), EmailFake())
