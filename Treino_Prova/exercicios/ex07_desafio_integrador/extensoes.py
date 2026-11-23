"""ex07 — Parte D. SEU ARQUIVO: estenda o sistema SEM editar loja.py."""
from loja import Opcional  # noqa: F401  (base para o seu decorador)


class FreteMotoboy:
    def calcular(self, peso_kg):
        raise NotImplementedError   # TODO D1


class ComSeguro(Opcional):
    pass                            # TODO D2


class ProcessadorPix:
    def processar(self, valor, token):
        raise NotImplementedError   # TODO D3
