"""
Aula 05 - SOLUCAO DE REFERENCIA (professor). NAO incluir no pacote do aluno.
Strategy: cada politica de tarifa e uma classe; a Reserva delega. 4 testes verdes.
"""

class TarifaComum:
    def aplicar(self, base):
        return base

class TarifaFidelidade:
    def aplicar(self, base):
        return base * 0.90

class TarifaParceiro:
    def aplicar(self, base):
        return base * 0.80

# desafio / extensao: tipo novo sem tocar na Reserva
class TarifaVIP:
    def aplicar(self, base):
        return base * 0.50

class Reserva:
    def __init__(self, diarias, valor_diaria, tarifa):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tarifa = tarifa

    def total(self):
        base = self.diarias * self.valor_diaria
        return self.tarifa.aplicar(base)

# Delimitacao (GIRIDHAR): em Python, a estrategia pode ser uma funcao:
#   def tarifa_vip(base): return base * 0.50
#   Reserva(2, 200, tarifa_vip)  -- se total() chamar self.tarifa(base)
# Usamos classes por clareza didatica; a funcao e a forma enxuta.
