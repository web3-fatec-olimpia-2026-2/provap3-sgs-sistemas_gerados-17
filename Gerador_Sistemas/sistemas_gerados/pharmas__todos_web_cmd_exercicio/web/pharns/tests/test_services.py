"""Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
import ast
import inspect
import textwrap
from decimal import Decimal

import pytest

from pharns.models import Pharm
from pharns.services import POLITICAS, PharmService


def novo(**mudancas):
    copia = {"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "produto": 'Produto 1', "idade": 0, "categoria": 'Categoria 1', "cosmeticos": 'Cosmeticos 1', "medicamentos": 'Medicamentos 1', "tipo": "comum"}
    copia.update(mudancas)
    return Pharm(**copia)  # objeto em memória: nem precisa de banco


@pytest.mark.parametrize("tipo, fator", [("comum", 1.0), ("especial", 0.9), ("parceiro", 0.8), ("vip", 0.5)])
def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
    obj = novo(tipo=tipo)
    assert PharmService().valor_final(obj) == round(float(obj.total) * fator, 2)


def test_todo_tipo_do_model_tem_politica():
    assert set(POLITICAS) == {chave for chave, _ in Pharm.TIPOS}


def test_resumo_soma_os_valores():
    itens, total = PharmService().resumo([novo(), novo(tipo="especial")])
    assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(PharmService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra
