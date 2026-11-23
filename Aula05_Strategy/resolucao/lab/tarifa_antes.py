# ANTES da refatoração — guardado só para comparar (é o código original do laboratório).
# O "smell": cada tipo novo de hóspede obriga a abrir a Reserva e mexer neste if/elif.


class Reserva:
    def __init__(self, diarias, valor_diaria, tipo_hospede):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tipo_hospede = tipo_hospede   # um TEXTO decide o comportamento

    def total(self):
        base = self.diarias * self.valor_diaria
        if self.tipo_hospede == "comum":
            return base
        elif self.tipo_hospede == "fidelidade":
            return base * 0.90
        elif self.tipo_hospede == "parceiro":
            return base * 0.80
        else:
            raise ValueError("tipo de hospede desconhecido")
