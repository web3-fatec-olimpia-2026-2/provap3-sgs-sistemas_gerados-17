# ANTES da refatoração (código original do laboratório) — guardado para provar que o
# recibo saiu IDÊNTICO depois de separar as responsabilidades.


class Reserva:
    def __init__(self, hospede, diarias, valor_diaria):
        self.hospede = hospede
        self.diarias = diarias
        self.valor_diaria = valor_diaria

    def total(self):                       # 1. regra de negócio
        return self.diarias * self.valor_diaria

    def formatar_recibo(self):             # 2. apresentação
        return (f"RECIBO\n{self.hospede}\n"
                f"{self.diarias} diarias\nTotal: R$ {self.total()}")

    def salvar_em_arquivo(self, caminho):  # 3. infraestrutura
        with open(caminho, "w") as f:
            f.write(self.formatar_recibo())
