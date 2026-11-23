# LAB Aula 06 - SRP: uma classe que faz coisas demais
#
# A classe Reserva abaixo faz TRES coisas: calcula o total (regra de negocio),
# formata o recibo (apresentacao) e salva em arquivo (infraestrutura).
# Sao tres motivos diferentes para mexer nela - viola o SRP (uma classe,
# uma responsabilidade).
#
# Sua tarefa (siga o ROTEIRO.md): separar em tres classes, mantendo o
# comportamento (o teste do recibo tem que continuar verde).


class Reserva:
    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria

    def total(self):
        return self.diarias * self.valor_diaria

    def formatar_recibo(self):
        return (f"RECIBO\n{self.hospede}\n"
                f"{self.diarias} diarias\nTotal: R$ {self.total()}")

    def salvar_em_arquivo(self, caminho):
        with open(caminho, "w") as f:
            f.write(self.formatar_recibo())

# --------------------------------------------------------------------------
# SUA TAREFA: separar em tres classes, cada uma com UMA responsabilidade:
#   - Reserva          -> so os dados e o total() (regra de negocio)
#   - ReciboFormatter  -> so o metodo formatar(reserva) (apresentacao)
#   - ArquivoRepository -> so o metodo salvar(texto, caminho) (infraestrutura)
# O recibo formatado tem que ser IDENTICO ao de antes.
# --------------------------------------------------------------------------
