"""
Testes do Decorator. Cada extra implementa a MESMA interface (preco/descricao)
e pode ser empilhado em qualquer ordem.
Rode:  python3 -m pytest -v
"""
from reserva import (
    ReservaBase, ComCafeDaManha, ComTransfer, ComLateCheckout,
)


def test_reserva_base():
    r = ReservaBase(diaria=200.0, noites=2)
    assert r.preco() == 400.0
    assert r.descricao() == "Reserva 2 noite(s)"


def test_um_extra_soma_e_descreve():
    r = ComCafeDaManha(ReservaBase(200.0, 2))
    assert r.preco() == 440.0                      # 400 + 40
    assert r.descricao() == "Reserva 2 noite(s) + cafe da manha"


def test_dois_extras_empilham():
    r = ComTransfer(ComCafeDaManha(ReservaBase(200.0, 2)))
    assert r.preco() == 520.0                      # 400 + 40 + 80
    assert r.descricao() == "Reserva 2 noite(s) + cafe da manha + transfer"


def test_tres_extras_empilham():
    r = ComLateCheckout(ComTransfer(ComCafeDaManha(ReservaBase(200.0, 1))))
    assert r.preco() == 380.0                      # 200 + 40 + 80 + 60
    assert "late checkout" in r.descricao()


def test_ordem_nao_muda_o_preco():
    a = ComTransfer(ComCafeDaManha(ReservaBase(500.0, 1)))
    b = ComCafeDaManha(ComTransfer(ReservaBase(500.0, 1)))
    assert a.preco() == b.preco() == 620.0         # 500 + 40 + 80


def test_so_um_extra_de_cada_vez():
    r = ComLateCheckout(ReservaBase(300.0, 3))
    assert r.preco() == 960.0                      # 900 + 60
    assert r.descricao() == "Reserva 3 noite(s) + late checkout"
