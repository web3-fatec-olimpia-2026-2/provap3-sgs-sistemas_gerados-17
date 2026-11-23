"""Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
import ast
import inspect
import textwrap
from decimal import Decimal

import pytest

from matriculas.models import Matricula
from matriculas.services import POLITICAS, MatriculaService


def novo(**mudancas):
    copia = {"aluno": 'Fernanda', "turma": 101, "meses": 2, "mensalidade": Decimal("100.00"), "tipo": "mensal"}
    copia.update(mudancas)
    return Matricula(**copia)  # objeto em memória: nem precisa de banco


@pytest.mark.parametrize("tipo, fator", [("mensal", 1.0), ("universitario", 0.7), ("corporativo", 0.8), ("familia", 0.6)])
def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
    obj = novo(tipo=tipo)
    assert MatriculaService().valor_final(obj) == round(float(obj.total) * fator, 2)


def test_todo_tipo_do_model_tem_politica():
    assert set(POLITICAS) == {chave for chave, _ in Matricula.TIPOS}


def test_resumo_soma_os_valores():
    itens, total = MatriculaService().resumo([novo(), novo(tipo="universitario")])
    assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(MatriculaService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra
