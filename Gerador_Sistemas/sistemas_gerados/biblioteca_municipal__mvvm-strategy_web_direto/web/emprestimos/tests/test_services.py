"""Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
import ast
import inspect
import textwrap
from decimal import Decimal

import pytest

from emprestimos.models import Emprestimo
from emprestimos.services import POLITICAS, EmprestimoService


def novo(**mudancas):
    copia = {"leitor": 'Beatriz', "exemplar": 101, "dias": 2, "taxa_dia": Decimal("2.50"), "tipo": "comum"}
    copia.update(mudancas)
    return Emprestimo(**copia)  # objeto em memória: nem precisa de banco


@pytest.mark.parametrize("tipo, fator", [("comum", 1.0), ("estudante", 0.5), ("professor", 0.7), ("visitante", 1.5)])
def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
    obj = novo(tipo=tipo)
    assert EmprestimoService().valor_final(obj) == round(float(obj.total) * fator, 2)


def test_todo_tipo_do_model_tem_politica():
    assert set(POLITICAS) == {chave for chave, _ in Emprestimo.TIPOS}


def test_resumo_soma_os_valores():
    itens, total = EmprestimoService().resumo([novo(), novo(tipo="estudante")])
    assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(EmprestimoService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra
