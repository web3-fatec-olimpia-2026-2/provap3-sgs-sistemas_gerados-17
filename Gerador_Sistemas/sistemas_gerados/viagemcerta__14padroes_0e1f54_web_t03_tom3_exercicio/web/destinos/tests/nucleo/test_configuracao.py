"""Testes do SINGLETON: um objeto só, visto por todos; na versão antiga as cópias divergem."""
import pytest

from destinos.nucleo import antes_configuracao
from destinos.nucleo.configuracao import Configuracao, formatar, total_com_taxa
from destinos.tests.nucleo.fabrica import criar


@pytest.fixture(autouse=True)
def configuracao_limpa():
    Configuracao.reiniciar()
    yield
    Configuracao.reiniciar()


def test_sempre_o_mesmo_objeto():
    assert Configuracao() is Configuracao()


def test_valores_iniciais():
    cfg = Configuracao()
    assert (cfg.moeda, cfg.taxa_servico) == ("R$", 0.0)


def test_mudanca_vale_para_todos():
    Configuracao().taxa_servico = 0.1
    item = criar()
    assert total_com_taxa(item) == round(item.total * 1.1, 2)


def test_chamar_de_novo_nao_apaga_o_que_mudou():
    Configuracao().moeda = "US$"
    Configuracao()
    assert formatar(10) == "US$ 10.00"


def test_reiniciar_comeca_do_zero():
    primeira = Configuracao()
    Configuracao.reiniciar()
    assert Configuracao() is not primeira


def test_antes_as_copias_divergem():
    item = criar()
    antes_configuracao.CONFIG_DO_CAIXA.taxa_servico = 0.1
    try:
        assert antes_configuracao.total_no_caixa(item) != antes_configuracao.total_no_relatorio(item)
    finally:
        antes_configuracao.CONFIG_DO_CAIXA.taxa_servico = 0.0
