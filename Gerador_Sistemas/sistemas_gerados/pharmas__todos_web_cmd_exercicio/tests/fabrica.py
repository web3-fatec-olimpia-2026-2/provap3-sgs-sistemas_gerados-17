"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a Pharm ganhar um atributo, só este arquivo muda.
"""
from nucleo.entidades import Pharm

DADOS_EXEMPLO = [
    {'cliente': 'Ana', 'codigo': 101, 'quantidade': 2, 'valor_unitario': 100.0, 'produto': 'Produto 1', 'idade': 0, 'categoria': 'Categoria 1', 'cosmeticos': 'Cosmeticos 1', 'medicamentos': 'Medicamentos 1'},
    {'cliente': 'Bruno', 'codigo': 201, 'quantidade': 3, 'valor_unitario': 49.9, 'produto': 'Produto 2', 'idade': 1, 'categoria': 'Categoria 2', 'cosmeticos': 'Cosmeticos 2', 'medicamentos': 'Medicamentos 2'},
    {'cliente': 'Carla', 'codigo': 301, 'quantidade': 1, 'valor_unitario': 250.0, 'produto': 'Produto 3', 'idade': 2, 'categoria': 'Categoria 3', 'cosmeticos': 'Cosmeticos 3', 'medicamentos': 'Medicamentos 3'},
    {'cliente': 'Diego', 'codigo': 401, 'quantidade': 4, 'valor_unitario': 0.0, 'produto': 'Produto 4', 'idade': 3, 'categoria': 'Categoria 4', 'cosmeticos': 'Cosmeticos 4', 'medicamentos': 'Medicamentos 4'}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma Pharm (válida, a menos que as mudanças a tornem inválida)."""
    return Pharm(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro Pharms diferentes e válidas — objetos novos a cada chamada."""
    return [Pharm(**d) for d in DADOS_EXEMPLO]
