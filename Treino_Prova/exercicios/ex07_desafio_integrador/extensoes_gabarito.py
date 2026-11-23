"""ex07 — Parte D, GABARITO comentado. Nenhuma linha de loja.py foi alterada (OCP)."""
from loja import Opcional


class FreteMotoboy:
    """D1 — nova ESTRATÉGIA de frete: mesma interface calcular(peso_kg).
    O PedidoService não muda porque só conhece a interface."""

    VALOR, LIMITE_KG = 12, 5

    def calcular(self, peso_kg):
        if peso_kg > self.LIMITE_KG:
            raise ValueError("motoboy leva até 5 kg")
        return self.VALOR


class ComSeguro(Opcional):
    """D2 — novo DECORADOR: mantém preco()/descricao(), chama o de dentro e acrescenta 3%.
    Como multiplica, a posição na pilha importa (igual ao cupom)."""

    TAXA = 0.03

    def preco(self):
        return round(self._pedido.preco() * (1 + self.TAXA), 2)

    def descricao(self):
        return self._pedido.descricao() + " + seguro"


class ProcessadorPix:
    """D3 — NÃO precisa de Adapter: o código é NOSSO, então já nasce falando a interface que o
    checkout espera (processar(valor, token)). Duck typing basta; Adapter aqui seria cerimônia."""

    def __init__(self):
        self._seq = 0

    def processar(self, valor, token):
        self._seq += 1
        return f"PIX-{self._seq:04d}"
