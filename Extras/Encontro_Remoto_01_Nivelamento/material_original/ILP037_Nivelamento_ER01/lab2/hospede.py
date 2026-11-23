# LAB 2 - Encapsulamento: proteja a idade do Hospede
#
# O Hospede ja esta pronto (voce o construiu no Lab 1).
# Agora ele tambem recebe uma IDADE - mas ela NAO esta protegida:
# hoje aceita qualquer numero, ate negativo.
#
# Sua tarefa (siga o ROTEIRO.md): proteger a idade com @property e setter.
# Regra: idade nao pode ser negativa.


class Hospede:
    def __init__(self, nome, documento, idade):
        self.nome = nome
        self.documento = documento
        self.idade = idade          # HOJE: guarda direto, sem proteger
        self.hospedado = False

    def fazer_check_in(self):
        self.hospedado = True

    # -------------------------------------------------------------------
    # SUA TAREFA: transforme a idade numa @property protegida.
    # Regra: se idade < 0, levante ValueError("idade nao pode ser negativa").
    #
    # Modelo (e assim que se protege um atributo):
    #   @property
    #   def idade(self):
    #       return self._idade
    #
    #   @idade.setter
    #   def idade(self, valor):
    #       if valor < 0:
    #           raise ValueError("idade nao pode ser negativa")
    #       self._idade = valor
    # -------------------------------------------------------------------
