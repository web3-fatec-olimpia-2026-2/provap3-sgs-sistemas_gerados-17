import pytest

from nucleo.comandos import AlterarCampo, Historico
from tests.fabrica import criar


def test_executar_muda_o_campo():
    item = criar()
    Historico().executar(AlterarCampo(item, "quantidade", item.quantidade + 1))
    assert item.quantidade == criar().quantidade + 1


def test_desfazer_volta_ao_valor_anterior():
    item = criar()
    historico = Historico()
    historico.executar(AlterarCampo(item, "quantidade", item.quantidade + 1))
    assert historico.desfazer() is True and vars(item) == vars(criar())


def test_desfaz_na_ordem_inversa_e_refaz():
    item = criar()
    q0 = item.quantidade
    historico = Historico()
    historico.executar(AlterarCampo(item, "quantidade", q0 + 1))
    historico.executar(AlterarCampo(item, "quantidade", q0 + 2))
    historico.desfazer()
    assert item.quantidade == q0 + 1
    historico.desfazer()
    assert item.quantidade == q0
    historico.refazer()
    assert item.quantidade == q0 + 1


def test_comando_invalido_nao_entra_no_historico():
    item = criar()
    historico = Historico()
    with pytest.raises(ValueError):
        historico.executar(AlterarCampo(item, "quantidade", 0))
    assert historico.acoes() == [] and historico.desfazer() is False


def test_acao_nova_apaga_o_refazer():
    item = criar()
    historico = Historico()
    historico.executar(AlterarCampo(item, "quantidade", item.quantidade + 1))
    historico.desfazer()
    historico.executar(AlterarCampo(item, "preco", item.preco + 1))
    assert historico.refazer() is False
