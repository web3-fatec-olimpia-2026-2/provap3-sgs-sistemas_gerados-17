"""Aula 07 — 2 testes originais + os meus (service sozinho, saída idêntica, API)."""
import ast
import inspect
import textwrap

import pytest

import relatorio_antes
from relatorio import (RESERVAS, RelatorioService, relatorio_reservas_api,
                       relatorio_reservas_view)


# --- originais ---
def test_saida_final():
    saida = relatorio_reservas_view(RESERVAS)
    assert "Ana: R$ 540.00" in saida
    assert "Bruno: R$ 300.00" in saida
    assert "TOTAL: R$ 840.00" in saida


def test_service_sem_http():
    svc = RelatorioService([{"hospede": "X", "diarias": 2, "valor": 100, "tipo": "fidelidade"}])
    linhas, total = svc.calcular()
    assert total == 180.0
    assert linhas == [("X", 180.0)]


# --- meus: a regra testada direto, caso a caso (barato → dá para testar muito) ---
@pytest.mark.parametrize("tipo, esperado", [
    ("comum", 500.0), ("fidelidade", 450.0), ("parceiro", 400.0), ("desconhecido", 500.0),
])
def test_desconto_por_tipo(tipo, esperado):
    linhas, total = RelatorioService(
        [{"hospede": "T", "diarias": 5, "valor": 100, "tipo": tipo}]).calcular()
    assert total == esperado


def test_lista_vazia():
    assert RelatorioService([]).calcular() == ([], 0)


def test_saida_identica_a_versao_faz_tudo():
    varias = RESERVAS + [{"hospede": "Caio", "diarias": 1, "valor": 99.99, "tipo": "parceiro"}]
    assert relatorio_reservas_view(varias) == relatorio_antes.relatorio_reservas_view(varias)


def test_service_nao_conhece_web():
    # Checagem estrutural: nenhum IDENTIFICADOR usado no código do service (variáveis,
    # parâmetros, atributos) fala de request/HTTP/template. Docstrings e comentários
    # não contam — o ast ignora comentários e aqui só olho nomes.
    arvore = ast.parse(textwrap.dedent(inspect.getsource(RelatorioService)))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name):
            nomes.add(no.id.lower())
        elif isinstance(no, ast.Attribute):
            nomes.add(no.attr.lower())
        elif isinstance(no, ast.arg):
            nomes.add(no.arg.lower())
    for palavra in ("request", "http", "template", "render"):
        assert not any(palavra in nome for nome in nomes), palavra


def test_mesma_regra_outra_apresentacao():
    dados = relatorio_reservas_api(RESERVAS)
    assert dados["total_geral"] == 840.0
    assert dados["itens"][0] == {"hospede": "Ana", "total": 540.0}
