"""Fábrica de objetos VÁLIDOS para todos os testes (gerada).

Centraliza os dados de exemplo: se a Matricula ganhar um atributo, só este arquivo muda.
"""
from nucleo.entidades import Matricula

DADOS_EXEMPLO = [
    {'aluno': 'Fernanda', 'turma': 101, 'meses': 2, 'mensalidade': 100.0},
    {'aluno': 'Gustavo', 'turma': 201, 'meses': 3, 'mensalidade': 150.0},
    {'aluno': 'Helena', 'turma': 301, 'meses': 1, 'mensalidade': 89.9},
    {'aluno': 'Igor', 'turma': 401, 'meses': 4, 'mensalidade': 0.0}
]


def dados(indice=0, **mudancas):
    """Cópia dos dados válidos nº `indice`, com as mudanças pedidas."""
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    """Cria uma Matricula (válida, a menos que as mudanças a tornem inválida)."""
    return Matricula(**dados(indice, **mudancas))


def itens_exemplo():
    """Quatro Matriculas diferentes e válidas — objetos novos a cada chamada."""
    return [Matricula(**d) for d in DADOS_EXEMPLO]
