"""Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
import ast
import inspect
import textwrap
from decimal import Decimal

import pytest

from citricultura.models import LoteCitros
from citricultura.services import POLITICAS, LoteCitrosService


def novo(**mudancas):
    copia = {"cooperado": 'Isabela', "talhao": 101, "caixas": 2, "preco_caixa": Decimal("38.00"), "cidade": 'Cidade 1', "tipo": "industria"}
    copia.update(mudancas)
    return LoteCitros(**copia)  # objeto em memória: nem precisa de banco


@pytest.mark.parametrize("tipo, fator", [("industria", 1.0), ("mesa", 1.25), ("exportacao", 1.4), ("refugo", 0.3)])
def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
    obj = novo(tipo=tipo)
    assert LoteCitrosService().valor_final(obj) == round(float(obj.total) * fator, 2)


def test_todo_tipo_do_model_tem_politica():
    assert set(POLITICAS) == {chave for chave, _ in LoteCitros.TIPOS}


def test_resumo_soma_os_valores():
    itens, total = LoteCitrosService().resumo([novo(), novo(tipo="mesa")])
    assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(LoteCitrosService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra
