# LAB Aula 05 - Strategy: refatorar o if/elif de tarifa
#
# A classe Reserva calcula o total aplicando um desconto por tipo de hospede.
# Hoje ela faz isso com um if/elif que CRESCE a cada novo tipo (o smell).
#
# Sua tarefa (siga o ROTEIRO.md): refatorar para Strategy, mantendo os testes
# verdes, e depois acrescentar um tipo novo SEM tocar na classe Reserva.


class Reserva:
    def __init__(self, diarias, valor_diaria, tipo_hospede):
        self.diarias = diarias
        self.valor_diaria = valor_diaria
        self.tipo_hospede = tipo_hospede

    def total(self):
        base = self.diarias * self.valor_diaria
        # o smell: cada tipo novo obriga a mexer AQUI dentro
        if self.tipo_hospede == "comum":
            return base
        elif self.tipo_hospede == "fidelidade":
            return base * 0.90
        elif self.tipo_hospede == "parceiro":
            return base * 0.80
        else:
            raise ValueError("tipo de hospede desconhecido")
