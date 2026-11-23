import pytest

from hw03a_segunda_property import Quarto


def test_numero_valido():
    assert Quarto(101, 250).numero == 101


@pytest.mark.parametrize("invalido", [0, -5, 2.5, "101", True])
def test_numero_invalido(invalido):
    q = Quarto(101, 250)
    with pytest.raises(ValueError):
        q.numero = invalido


def test_diaria_continua_protegida():
    with pytest.raises(ValueError):
        Quarto(101, -1)


def test_diaria_aceita_zero_mas_numero_nao():
    assert Quarto(101, 0).diaria == 0
    with pytest.raises(ValueError):
        Quarto(0, 100)
