"""Testes do SERVICE web: regra sem HTTP, reaproveitando o Strategy do núcleo."""
import ast
import inspect
import textwrap
from decimal import Decimal

import pytest

from apps.petshops.models import Petshop
from apps.petshops.services import POLITICAS, PetshopService


def novo(**mudancas):
    copia = {"cliente": 'Ana', "codigo": 101, "quantidade": 2, "valor_unitario": Decimal("100.00"), "tipo": "comum"}
    copia.update(mudancas)
    return Petshop(**copia)  # objeto em memória: nem precisa de banco


@pytest.mark.parametrize("tipo, fator", [("comum", 1.0), ("especial", 0.9), ("parceiro", 0.8), ("vip", 0.5)])
def test_valor_final_usa_a_politica_do_nucleo(tipo, fator):
    obj = novo(tipo=tipo)
    assert PetshopService().valor_final(obj) == round(float(obj.total) * fator, 2)


def test_todo_tipo_do_model_tem_politica():
    assert set(POLITICAS) == {chave for chave, _ in Petshop.TIPOS}


def test_resumo_soma_os_valores():
    itens, total = PetshopService().resumo([novo(), novo(tipo="especial")])
    assert len(itens) == 2 and total == round(sum(v for _, v in itens), 2)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(PetshopService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra
