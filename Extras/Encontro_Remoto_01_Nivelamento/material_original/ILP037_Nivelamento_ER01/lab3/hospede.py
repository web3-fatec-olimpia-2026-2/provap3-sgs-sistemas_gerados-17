# LAB 3 - Heranca: o HospedeVIP e-um Hospede
#
# O Hospede ja esta pronto e protegido (Labs 1 e 2).
# Sua tarefa: criar a classe HospedeVIP, que E-UM Hospede com um beneficio a mais:
# um numero de pontos de fidelidade.
#
# Siga o ROTEIRO.md. Voce vai usar heranca e super().


class Hospede:
    def __init__(self, nome, documento, idade):
        self.nome = nome
        self.documento = documento
        self.idade = idade
        self.hospedado = False

    def fazer_check_in(self):
        self.hospedado = True

    @property
    def idade(self):
        return self._idade

    @idade.setter
    def idade(self, valor):
        if valor < 0:
            raise ValueError("idade nao pode ser negativa")
        self._idade = valor


# -----------------------------------------------------------------------
# SUA TAREFA: criar HospedeVIP, que E-UM Hospede.
# Um HospedeVIP tem tudo que o Hospede tem (nome, documento, idade,
# fazer_check_in) MAIS um atributo: pontos.
#
# Dica de estrutura:
#   class HospedeVIP(Hospede):                      # E-UM Hospede
#       def __init__(self, nome, documento, idade, pontos):
#           super().__init__(nome, documento, idade)   # reaproveita o Hospede
#           self.pontos = pontos
# -----------------------------------------------------------------------
