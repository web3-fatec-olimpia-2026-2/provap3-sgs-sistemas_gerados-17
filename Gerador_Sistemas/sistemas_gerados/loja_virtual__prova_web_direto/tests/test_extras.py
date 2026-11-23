"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.extras import Adicional, PedidoBase, ComCartao, ComCupom10, ComEmbrulho, ComEntregaExpressa
from tests.fabrica import criar

FLAGS = {ComEmbrulho: "embrulho", ComCartao: "cartao", ComEntregaExpressa: "entrega_expressa"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


def test_componente_entrega_o_total():
    item = criar()
    assert PedidoBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(PedidoBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComCartao(ComEmbrulho(PedidoBase(item)))
    base = f"Pedido de {item.cliente} ({item.quantidade} unidade(s))"
    assert componente.descricao() == base + " + embrulho para presente" + " + cartão"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComEmbrulho(ComEmbrulho(PedidoBase(item))).preco() == pytest.approx(item.total + 2 * 15.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComCupom10(ComEmbrulho(PedidoBase(item)))
    por_dentro = ComEmbrulho(ComCupom10(PedidoBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 15.0) * 0.9, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 0.9, 2) + 15.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComEmbrulho, ComCartao, ComEntregaExpressa, ComCupom10])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(PedidoBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
