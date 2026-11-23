"""Extra — a mesma ideia com uma INTERFACE formal (módulo abc).

Na versão do laboratório, a classe Quarto tem um preço padrão (200). Às vezes não existe
"padrão" que faça sentido: toda forma de pagamento PRECISA dizer como calcula. Aí usamos
uma classe abstrata: ela declara o contrato e o Python impede criar um subtipo que esqueça
de implementá-lo. (Prévia do que a Aula 05 usa no Strategy.)
"""
from abc import ABC, abstractmethod


class FormaPagamento(ABC):
    """Contrato: toda forma de pagamento sabe calcular o valor final."""

    @abstractmethod
    def valor_final(self, valor):
        """Subclasses OBRIGATORIAMENTE implementam."""


class Pix(FormaPagamento):
    def valor_final(self, valor):
        return round(valor * 0.95, 2)       # 5% de desconto


class Cartao(FormaPagamento):
    def valor_final(self, valor):
        return round(valor * 1.03, 2)       # 3% de taxa


class Boleto(FormaPagamento):
    TARIFA = 2.50

    def valor_final(self, valor):
        return round(valor + self.TARIFA, 2)


def cobrar(forma: FormaPagamento, valor):
    # Função polimórfica: só conhece o contrato, nunca o tipo concreto.
    return forma.valor_final(valor)
