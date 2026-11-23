"""ex01 — Strategy: frete da loja. SEU ARQUIVO (resolva os TODOs; não mexa no PedidoAntigo)."""


# ---------------------------------------------------------------------------
# O SMELL (pronto — é a referência de comportamento)
# ---------------------------------------------------------------------------
class PedidoAntigo:
    def __init__(self, peso_kg, tipo_frete):
        self.peso_kg = peso_kg
        self.tipo_frete = tipo_frete

    def frete(self):
        if self.tipo_frete == "pac":
            return 10 + 2 * self.peso_kg
        elif self.tipo_frete == "sedex":
            return 20 + 4 * self.peso_kg
        elif self.tipo_frete == "retirada":
            return 0
        else:
            raise ValueError("tipo de frete desconhecido")


# ---------------------------------------------------------------------------
# TODO 1: estratégias com calcular(peso_kg)
# ---------------------------------------------------------------------------
class FretePAC:
    def calcular(self, peso_kg):
        raise NotImplementedError   # TODO


class FreteSedex:
    def calcular(self, peso_kg):
        raise NotImplementedError   # TODO


class RetiradaNaLoja:
    def calcular(self, peso_kg):
        raise NotImplementedError   # TODO


# ---------------------------------------------------------------------------
# TODO 2: o contexto recebe a estratégia e delega (sem if)
# ---------------------------------------------------------------------------
class Pedido:
    def __init__(self, peso_kg, frete):
        raise NotImplementedError   # TODO

    def frete(self):
        raise NotImplementedError   # TODO


# ---------------------------------------------------------------------------
# TODO 3: estratégia nova SEM tocar em Pedido
# ---------------------------------------------------------------------------
class FreteMotoboy:
    def calcular(self, peso_kg):
        raise NotImplementedError   # TODO: 15 fixo até 5 kg; acima → ValueError
