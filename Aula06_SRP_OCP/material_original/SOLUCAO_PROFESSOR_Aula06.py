"""
Aula 06 - SOLUCAO DE REFERENCIA (professor). NAO incluir no pacote do aluno.
SRP: Reserva (dados+total) / ReciboFormatter (apresentacao) / ArquivoRepository (persistencia).
2 testes verdes. O recibo e identico ao da versao "faz-tudo".
"""

class Reserva:
    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria
    def total(self):
        return self.diarias * self.valor_diaria

class ReciboFormatter:
    def formatar(self, reserva):
        return (f"RECIBO\n{reserva.hospede}\n"
                f"{reserva.diarias} diarias\nTotal: R$ {reserva.total()}")

class ArquivoRepository:
    def salvar(self, texto, caminho):
        with open(caminho, "w") as f:
            f.write(texto)

# Ligacao com OCP (Aula 05): o Strategy da politica de tarifa e o OCP na pratica -
# adicionar uma TarifaVIP nova sem tocar na Reserva. SRP separa; OCP estende sem modificar.
