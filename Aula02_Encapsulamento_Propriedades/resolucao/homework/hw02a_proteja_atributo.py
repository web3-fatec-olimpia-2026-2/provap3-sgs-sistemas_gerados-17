"""Homework 02a — Proteja um atributo.

Parti da classe do Homework 01 (Bicicleta) e protegi o atributo que TEM regra:
`marcha_atual`, que só pode ir de 1 até o total de marchas da bicicleta.
"""


class Bicicleta:
    TOTAL_MARCHAS = 21

    def __init__(self, marca, marcha_atual=1):
        self.marca = marca              # texto livre, sem regra → atributo simples (sem @property)
        self.marcha_atual = marcha_atual  # passa pelo setter abaixo → validado na criação
        self.velocidade = 0

    @property
    def marcha_atual(self):
        """Getter: devolve a marcha guardada no atributo interno."""
        return self._marcha_atual

    @marcha_atual.setter
    def marcha_atual(self, nova):
        """Setter: só grava se a marcha existir nesta bicicleta."""
        # Checo o tipo também: "3" (texto) ou 2.5 não são marchas.
        if not isinstance(nova, int) or not 1 <= nova <= self.TOTAL_MARCHAS:
            raise ValueError(f"marcha deve ser um inteiro entre 1 e {self.TOTAL_MARCHAS}")
        self._marcha_atual = nova

    def pedalar(self):
        self.velocidade += self.marcha_atual


# Regra protegida: a marcha atual precisa existir (1 a 21) — não há marcha 0, negativa ou 30.
# Escolhi `marcha_atual` porque é o único atributo com regra clara; `marca` é texto livre
# e protegê-lo seria só peso. `velocidade` muda só por métodos internos (pedalar/frear).
