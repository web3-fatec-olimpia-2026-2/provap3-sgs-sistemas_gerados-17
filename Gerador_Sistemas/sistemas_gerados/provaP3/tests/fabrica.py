"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a LoteCitros ganhar um atributo, só este arquivo muda.
"""
from nucleo.entidades import LoteCitros

DADOS_EXEMPLO = [
    {'cooperado': 'Isabela', 'talhao': 101, 'caixas': 2, 'preco_caixa': 38.0, 'cidade': 'Cidade 1', 'cpf_cnpj_provap3': 'Cpf cnpj provap3 1'},
    {'cooperado': 'João', 'talhao': 201, 'caixas': 3, 'preco_caixa': 32.0, 'cidade': 'Cidade 2', 'cpf_cnpj_provap3': 'Cpf cnpj provap3 2'},
    {'cooperado': 'Karina', 'talhao': 301, 'caixas': 1, 'preco_caixa': 52.0, 'cidade': 'Cidade 3', 'cpf_cnpj_provap3': 'Cpf cnpj provap3 3'},
    {'cooperado': 'Lucas', 'talhao': 401, 'caixas': 4, 'preco_caixa': 0.0, 'cidade': 'Cidade 4', 'cpf_cnpj_provap3': 'Cpf cnpj provap3 4'}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma LoteCitros (válida, a menos que as mudanças a tornem inválida)."""
    return LoteCitros(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro LoteCitross diferentes e válidas — objetos novos a cada chamada."""
    return [LoteCitros(**d) for d in DADOS_EXEMPLO]
