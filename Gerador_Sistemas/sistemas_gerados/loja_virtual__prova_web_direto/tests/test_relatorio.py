"""Testes do SERVICE: saída idêntica à view faz-tudo e regra testada sem HTTP."""
import ast
import inspect
import textwrap

import pytest

from nucleo.relatorio import REGISTROS, RelatorioService, relatorio_api, relatorio_view


@pytest.mark.parametrize("tipo, fator", [("comum", 1.0), ("fidelidade", 0.9), ("atacado", 0.85)])
def test_regra_testada_direto_sem_http(tipo, fator):
    _, total = RelatorioService([{"nome": "T", "quantidade": 2, "preco": 100.0, "tipo": tipo}]).calcular()
    assert total == pytest.approx(200.0 * fator)


def test_tipo_desconhecido_fica_sem_desconto():
    _, total = RelatorioService([{"nome": "T", "quantidade": 2, "preco": 100.0, "tipo": "???"}]).calcular()
    assert total == 200.0


def test_lista_vazia():
    assert RelatorioService([]).calcular() == ([], 0)


def test_service_nao_conhece_web():
    arvore = ast.parse(textwrap.dedent(inspect.getsource(RelatorioService)))
    nomes = {n.id.lower() for n in ast.walk(arvore) if isinstance(n, ast.Name)}
    nomes |= {n.attr.lower() for n in ast.walk(arvore) if isinstance(n, ast.Attribute)}
    nomes |= {n.arg.lower() for n in ast.walk(arvore) if isinstance(n, ast.arg)}
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra


def test_mesma_regra_outra_apresentacao():
    _, total = RelatorioService(REGISTROS).calcular()
    assert relatorio_api(REGISTROS)["total_geral"] == round(total, 2)
