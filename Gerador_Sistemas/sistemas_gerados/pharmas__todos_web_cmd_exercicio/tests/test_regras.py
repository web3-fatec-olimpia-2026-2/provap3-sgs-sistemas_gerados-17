"""Testes do INTERPRETER: o texto interpretado = a regra no código; regra nova sem programar."""
import pytest

from nucleo.antes_regras import regra_antiga
from nucleo.regras import E, Comparacao, Ou, ler_regra
from tests.fabrica import criar, itens_exemplo

REGRA = "quantidade >= 3 e total > 500 ou valor_unitario == 0"


@pytest.mark.parametrize("indice", range(4))
def test_texto_interpretado_igual_a_regra_no_codigo(indice):
    item = itens_exemplo()[indice]
    assert ler_regra(REGRA).interpretar(item) == regra_antiga(item)


@pytest.mark.parametrize("qtd, preco", [(1, 1000.0), (3, 100.0), (3, 300.0), (4, 0.0), (1, 0.0)])
def test_casos_variados(qtd, preco):
    item = criar(quantidade=qtd, valor_unitario=preco)
    assert ler_regra(REGRA).interpretar(item) == regra_antiga(item)


def test_arvore_montada_a_mao_equivale_ao_texto():
    arvore = Ou(E(Comparacao("quantidade", ">=", 3), Comparacao("total", ">", 500)),
                E(Comparacao("valor_unitario", "==", 0)))
    for item in itens_exemplo():
        assert arvore.interpretar(item) == ler_regra(REGRA).interpretar(item)


def test_regra_nova_sem_mudar_codigo():
    item = criar(quantidade=2, valor_unitario=50.0)
    assert ler_regra("total <= 100").interpretar(item) is True
    assert ler_regra("quantidade > 2").interpretar(item) is False


@pytest.mark.parametrize("ruim", ["total >", "campo_inexistente > 3", "total ~ 3", "total > muito"])
def test_regra_mal_escrita_e_recusada(ruim):
    with pytest.raises(ValueError):
        ler_regra(ruim)
