"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a Cooperado ganhar um atributo, só este arquivo muda.
"""
from cooperados.nucleo.entidades import Cooperado

DADOS_EXEMPLO = [
    {'cliente': 'Ana', 'codigo': 101, 'quantidade': 2, 'valor_unitario': 100.0},
    {'cliente': 'Bruno', 'codigo': 201, 'quantidade': 3, 'valor_unitario': 49.9},
    {'cliente': 'Carla', 'codigo': 301, 'quantidade': 1, 'valor_unitario': 250.0},
    {'cliente': 'Diego', 'codigo': 401, 'quantidade': 4, 'valor_unitario': 0.0}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma Cooperado (válida, a menos que as mudanças a tornem inválida)."""
    return Cooperado(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro Cooperados diferentes e válidas — objetos novos a cada chamada."""
    return [Cooperado(**d) for d in DADOS_EXEMPLO]
