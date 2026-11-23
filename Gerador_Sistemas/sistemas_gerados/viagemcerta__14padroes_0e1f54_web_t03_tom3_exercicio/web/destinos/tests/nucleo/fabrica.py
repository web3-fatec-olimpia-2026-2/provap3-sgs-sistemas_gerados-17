"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a Destino ganhar um atributo, só este arquivo muda.
"""
from destinos.nucleo.entidades import Destino

DADOS_EXEMPLO = [
    {'cliente': 'Ana', 'codigo': 101, 'quantidade': 2, 'valor_unitario': 100.0, 'cidade': 'Cidade 1', 'pais': 'Pais 1'},
    {'cliente': 'Bruno', 'codigo': 201, 'quantidade': 3, 'valor_unitario': 49.9, 'cidade': 'Cidade 2', 'pais': 'Pais 2'},
    {'cliente': 'Carla', 'codigo': 301, 'quantidade': 1, 'valor_unitario': 250.0, 'cidade': 'Cidade 3', 'pais': 'Pais 3'},
    {'cliente': 'Diego', 'codigo': 401, 'quantidade': 4, 'valor_unitario': 0.0, 'cidade': 'Cidade 4', 'pais': 'Pais 4'}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma Destino (válida, a menos que as mudanças a tornem inválida)."""
    return Destino(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro Destinos diferentes e válidas — objetos novos a cada chamada."""
    return [Destino(**d) for d in DADOS_EXEMPLO]
