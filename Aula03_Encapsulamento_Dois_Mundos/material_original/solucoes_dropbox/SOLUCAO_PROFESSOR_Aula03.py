"""
ILP-037 Aula 03 - SOLUCAO DE REFERENCIA (uso do professor).
NAO INCLUIR no pacote do aluno.

Quarto completo: diaria e capacidade protegidas + desafio receita_maxima.
Todos os 4 testes passam; o desafio da 500.
"""


class Quarto:
    def __init__(self, numero, diaria, capacidade):
        self.numero = numero
        self.diaria = diaria
        self.capacidade = capacidade

    @property
    def diaria(self):
        return self._diaria

    @diaria.setter
    def diaria(self, valor):
        if valor < 0:
            raise ValueError("diaria nao pode ser negativa")
        self._diaria = valor

    @property
    def capacidade(self):
        return self._capacidade

    @capacidade.setter
    def capacidade(self, valor):
        if valor < 1:
            raise ValueError("capacidade minima e 1")
        self._capacidade = valor

    # --- desafio ---
    @property
    def receita_maxima(self):
        return self.diaria * self.capacidade
