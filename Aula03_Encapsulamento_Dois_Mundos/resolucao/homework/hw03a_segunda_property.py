"""Homework 03a — Proteja um segundo atributo.

Partindo da classe Quarto (que já protegia a diária), protegi um SEGUNDO atributo
com regra própria: o `numero` do quarto, que precisa ser um inteiro positivo.
(A capacidade já foi feita no laboratório — aqui escolhi outro para praticar.)
"""


class Quarto:
    def __init__(self, numero, diaria):
        self.numero = numero    # → setter de numero
        self.diaria = diaria    # → setter de diaria

    # --- 1º atributo protegido: diaria ---
    @property
    def diaria(self):
        return self._diaria

    @diaria.setter
    def diaria(self, valor):
        if valor < 0:
            raise ValueError("diaria nao pode ser negativa")
        self._diaria = valor

    # --- 2º atributo protegido: numero ---
    @property
    def numero(self):
        return self._numero

    @numero.setter
    def numero(self, valor):
        # bool é subclasse de int em Python (True == 1), por isso excluo explicitamente.
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("numero do quarto deve ser um inteiro positivo")
        self._numero = valor


# Regra do 2º atributo: o número do quarto é um INTEIRO maior que zero (não existe quarto 0, -5 ou "101A").
# É diferente da diária porque a diária é DINHEIRO (aceita 0 e decimais, só não negativo); o número é um IDENTIFICADOR.


if __name__ == "__main__":
    q = Quarto(101, 250)
    print(q.numero, q.diaria)
    try:
        q.numero = 0
    except ValueError as erro:
        print("barrado:", erro)
