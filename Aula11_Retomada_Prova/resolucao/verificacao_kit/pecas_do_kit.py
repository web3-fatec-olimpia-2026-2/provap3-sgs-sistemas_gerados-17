"""Peças mínimas usadas no Kit de Revisão, para CONFERIR as previsões rodando.

Primeiro preveja no papel (é o que a P3 pede); depois rode os testes desta pasta.
"""


# --- Decorator (Partes 2.1 e 3.1) -----------------------------------------
class ReservaBase:
    def __init__(self, diaria, noites):
        self.diaria, self.noites = diaria, noites

    def preco(self):
        return self.diaria * self.noites


class ServicoExtra:
    def __init__(self, reserva):
        self._reserva = reserva

    def preco(self):
        return self._reserva.preco()     # por padrão só DELEGA


class ComCafeDaManha(ServicoExtra):
    PRECO = 40.0

    def preco(self):
        return self._reserva.preco() + self.PRECO   # delega E soma a sua parte


class ComTransfer(ServicoExtra):
    PRECO = 80.0

    def preco(self):
        return self._reserva.preco() + self.PRECO


class ComCafeDaManhaComErro(ServicoExtra):
    """O erro da Parte 3.1: esqueceu de somar — só delega."""

    def preco(self):
        return self._reserva.preco()


# --- Strategy (Parte 2.2) --------------------------------------------------
class TarifaParceiro:
    def calcular(self, diaria):
        return diaria * 0.8


class Reserva:
    def __init__(self, diaria, tarifa):
        self.diaria, self.tarifa = diaria, tarifa

    def total(self):
        return self.tarifa.calcular(self.diaria)
