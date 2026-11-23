"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.antes_extras import preco_com_flags
from nucleo.extras import Adicional, ReservaBase, ComCafeDaManha, ComDescontoFidelidade, ComLateCheckout, ComTransfer
from tests.fabrica import criar

FLAGS = {ComCafeDaManha: "cafe_da_manha", ComTransfer: "transfer", ComLateCheckout: "late_checkout"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


@pytest.mark.parametrize("combinacao", COMBINACOES)
def test_qualquer_combinacao_bate_com_as_flags(combinacao):
    item = criar()
    componente = ReservaBase(item)
    for extra in combinacao:
        componente = extra(componente)
    esperado = preco_com_flags(item, **{FLAGS[e]: True for e in combinacao})
    assert componente.preco() == pytest.approx(esperado)


def test_componente_entrega_o_total():
    item = criar()
    assert ReservaBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(ReservaBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComTransfer(ComCafeDaManha(ReservaBase(item)))
    base = f"Reserva de {item.hospede} ({item.diarias} diária(s))"
    assert componente.descricao() == base + " + café da manhã" + " + transfer"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComCafeDaManha(ComCafeDaManha(ReservaBase(item))).preco() == pytest.approx(item.total + 2 * 40.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComDescontoFidelidade(ComCafeDaManha(ReservaBase(item)))
    por_dentro = ComCafeDaManha(ComDescontoFidelidade(ReservaBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 40.0) * 0.9, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 0.9, 2) + 40.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComCafeDaManha, ComTransfer, ComLateCheckout, ComDescontoFidelidade])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(ReservaBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
