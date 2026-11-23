"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a Viagcert ganhar um atributo, só este arquivo muda.
"""
from nucleo.entidades import Viagcert

DADOS_EXEMPLO = [
    {'viajante': 'Elisa', 'voo': 101, 'noites': 2, 'valor_noite': 350.0},
    {'viajante': 'Fábio', 'voo': 201, 'noites': 3, 'valor_noite': 280.0},
    {'viajante': 'Gabriela', 'voo': 301, 'noites': 1, 'valor_noite': 520.0},
    {'viajante': 'Henrique', 'voo': 401, 'noites': 4, 'valor_noite': 0.0}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma Viagcert (válida, a menos que as mudanças a tornem inválida)."""
    return Viagcert(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro Viagcerts diferentes e válidas — objetos novos a cada chamada."""
    return [Viagcert(**d) for d in DADOS_EXEMPLO]
