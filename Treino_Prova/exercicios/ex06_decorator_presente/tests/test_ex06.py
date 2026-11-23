import importlib
import itertools
import os

import pytest

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))

FLAGS = {"ComEmbrulho": "embrulho", "ComCartao": "cartao", "ComEntregaExpressa": "expressa"}


@pytest.mark.parametrize("combo", [c for n in range(4) for c in itertools.combinations(FLAGS, n)])
def test_todas_as_combinacoes_batem_com_as_flags(combo):
    p = m.PedidoBase(100)
    for nome in combo:
        p = getattr(m, nome)(p)
    assert p.preco() == m.preco_com_flags(100, **{FLAGS[n]: True for n in combo})


def test_descricao_segue_a_ordem_do_embrulho():
    p = m.ComEntregaExpressa(m.ComEmbrulho(m.PedidoBase(100)))
    assert p.descricao() == "Pedido R$ 100.00 + embrulho + entrega expressa"


def test_dois_cartoes():
    assert m.ComCartao(m.ComCartao(m.PedidoBase(100))).preco() == 110


def test_cupom_ordem_importa():
    por_fora = m.ComCupom10(m.ComEntregaExpressa(m.PedidoBase(100)))   # (100+25)*0.9
    por_dentro = m.ComEntregaExpressa(m.ComCupom10(m.PedidoBase(100)))  # 100*0.9+25
    assert por_fora.preco() == 112.5
    assert por_dentro.preco() == 115.0
    assert por_fora.descricao().endswith("(-10% cupom)")


def test_decorador_base_so_delega():
    assert m.Opcional(m.PedidoBase(80)).preco() == 80
