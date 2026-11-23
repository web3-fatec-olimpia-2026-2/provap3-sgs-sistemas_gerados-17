"""Homework 01 — Meu objeto do dia a dia.

Enunciado (slide 32 da Aula 01):
    Escolha uma entidade do seu cotidiano (não pode ser hóspede, quarto ou reserva)
    e descreva: nome da classe, TRÊS atributos e TRÊS métodos.

Entidade escolhida: Bicicleta.
    Atributos: marca, marcha_atual, velocidade
    Métodos:   pedalar(), frear(), trocar_marcha()

Rodar:  python hw01_meu_objeto.py      (demonstração)
        python -m pytest -v            (testes)
"""


class Bicicleta:
    """Uma bicicleta de marchas.

    A CLASSE é a "planta": diz que toda bicicleta tem marca, marcha e velocidade,
    e que sabe pedalar, frear e trocar de marcha. Cada bicicleta criada com
    Bicicleta(...) é um OBJETO com os seus próprios valores.
    """

    # Constante de classe: vale para todas as bicicletas (não é estado de um objeto).
    TOTAL_MARCHAS = 21

    def __init__(self, marca):
        # __init__ é o construtor: roda uma vez, quando o objeto nasce.
        # "self" é o próprio objeto que está sendo criado.
        self.marca = marca          # atributo 1 — de quem é a bicicleta
        self.marcha_atual = 1       # atributo 2 — toda bicicleta começa na 1ª marcha
        self.velocidade = 0         # atributo 3 — começa parada (km/h)

    def pedalar(self):
        """Aumenta a velocidade. Marcha mais alta = ganho maior por pedalada."""
        # Uso self.velocidade (atributo do objeto). Se eu escrevesse só
        # "velocidade = ...", criaria uma variável local que morre aqui —
        # o erro mais comum apontado no slide 23.
        self.velocidade += self.marcha_atual

    def frear(self):
        """Reduz a velocidade pela metade; nunca fica negativa."""
        self.velocidade = self.velocidade // 2

    def trocar_marcha(self, nova_marcha):
        """Troca a marcha, desde que exista nessa bicicleta."""
        # O próprio objeto protege a sua regra: não existe marcha 0 nem 22.
        if not 1 <= nova_marcha <= self.TOTAL_MARCHAS:
            raise ValueError(f"marcha deve estar entre 1 e {self.TOTAL_MARCHAS}")
        self.marcha_atual = nova_marcha


if __name__ == "__main__":
    # Uma classe, dois objetos — cada um com o SEU estado.
    caloi = Bicicleta("Caloi")
    monark = Bicicleta("Monark")

    caloi.trocar_marcha(3)
    caloi.pedalar()          # só a caloi acelera
    caloi.pedalar()

    print(caloi.marca, caloi.velocidade)    # Caloi 6
    print(monark.marca, monark.velocidade)  # Monark 0  -> estado é do objeto
