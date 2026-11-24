"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.antes_extras import preco_com_flags
from nucleo.extras import Adicional, LoteCitrosBase, ComBonusQualidade, ComCamaraFria, ComClassificacao, ComFrete
from tests.fabrica import criar

FLAGS = {ComFrete: "frete", ComClassificacao: "classificacao", ComCamaraFria: "camara_fria"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


@pytest.mark.parametrize("combinacao", COMBINACOES)
def test_qualquer_combinacao_bate_com_as_flags(combinacao):
    item = criar()
    componente = LoteCitrosBase(item)
    for extra in combinacao:
        componente = extra(componente)
    esperado = preco_com_flags(item, **{FLAGS[e]: True for e in combinacao})
    assert componente.preco() == pytest.approx(esperado)


def test_componente_entrega_o_total():
    item = criar()
    assert LoteCitrosBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(LoteCitrosBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComClassificacao(ComFrete(LoteCitrosBase(item)))
    base = f"LoteCitros de {item.cooperado} ({item.caixas} caixa(s))"
    assert componente.descricao() == base + " + frete até a indústria" + " + classificação por calibre"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComFrete(ComFrete(LoteCitrosBase(item))).preco() == pytest.approx(item.total + 2 * 120.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComBonusQualidade(ComFrete(LoteCitrosBase(item)))
    por_dentro = ComFrete(ComBonusQualidade(LoteCitrosBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 120.0) * 1.1, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 1.1, 2) + 120.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComFrete, ComClassificacao, ComCamaraFria, ComBonusQualidade])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(LoteCitrosBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
