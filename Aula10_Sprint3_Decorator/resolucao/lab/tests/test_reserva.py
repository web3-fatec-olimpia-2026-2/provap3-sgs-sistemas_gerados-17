"""Lab Decorator — 6 testes ORIGINAIS + os meus."""
import itertools

import pytest

from reserva import (ComCafeDaManha, ComDescontoFidelidade, ComLateCheckout,
                     ComTransfer, ReservaBase, preco_com_extras)


# --- originais ---
def test_reserva_base():
    r = ReservaBase(diaria=200.0, noites=2)
    assert r.preco() == 400.0
    assert r.descricao() == "Reserva 2 noite(s)"


def test_um_extra_soma_e_descreve():
    r = ComCafeDaManha(ReservaBase(200.0, 2))
    assert r.preco() == 440.0
    assert r.descricao() == "Reserva 2 noite(s) + cafe da manha"


def test_dois_extras_empilham():
    r = ComTransfer(ComCafeDaManha(ReservaBase(200.0, 2)))
    assert r.preco() == 520.0
    assert r.descricao() == "Reserva 2 noite(s) + cafe da manha + transfer"


def test_tres_extras_empilham():
    r = ComLateCheckout(ComTransfer(ComCafeDaManha(ReservaBase(200.0, 1))))
    assert r.preco() == 380.0
    assert "late checkout" in r.descricao()


def test_ordem_nao_muda_o_preco():
    a = ComTransfer(ComCafeDaManha(ReservaBase(500.0, 1)))
    b = ComCafeDaManha(ComTransfer(ReservaBase(500.0, 1)))
    assert a.preco() == b.preco() == 620.0


def test_so_um_extra_de_cada_vez():
    r = ComLateCheckout(ReservaBase(300.0, 3))
    assert r.preco() == 960.0
    assert r.descricao() == "Reserva 3 noite(s) + late checkout"


# --- meus ---
FLAGS = {ComCafeDaManha: "cafe", ComTransfer: "transfer", ComLateCheckout: "late"}


@pytest.mark.parametrize("combo", [
    c for n in range(4) for c in itertools.combinations(FLAGS, n)
])
def test_decorator_bate_com_a_versao_de_flags(combo):
    # Todas as 8 combinações de extras: o embrulho dá o mesmo preço que as flags.
    r = ReservaBase(200.0, 2)
    for extra in combo:
        r = extra(r)
    flags = {FLAGS[e]: True for e in combo}
    assert r.preco() == preco_com_extras(200.0, 2, **flags)


def test_mesmo_extra_duas_vezes():
    # Dois cafés (ex.: dois hóspedes) — impossível com flag booleana.
    r = ComCafeDaManha(ComCafeDaManha(ReservaBase(100.0, 1)))
    assert r.preco() == 180.0


def test_decorador_que_muda_comportamento_a_ordem_importa():
    desc_depois = ComDescontoFidelidade(ComTransfer(ReservaBase(200.0, 1)))   # (200+80)*0.9
    desc_antes = ComTransfer(ComDescontoFidelidade(ReservaBase(200.0, 1)))    # 200*0.9+80
    assert desc_depois.preco() == 252.0
    assert desc_antes.preco() == 260.0
