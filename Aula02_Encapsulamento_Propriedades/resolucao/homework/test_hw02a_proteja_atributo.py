import pytest

from hw02a_proteja_atributo import Bicicleta


def test_marcha_valida_e_aceita():
    b = Bicicleta("Caloi", 5)
    assert b.marcha_atual == 5


@pytest.mark.parametrize("invalida", [0, -1, 22, "3", 2.5])
def test_marcha_invalida_levanta_value_error(invalida):
    b = Bicicleta("Caloi")
    with pytest.raises(ValueError):
        b.marcha_atual = invalida


def test_marcha_invalida_barrada_na_criacao():
    with pytest.raises(ValueError):
        Bicicleta("Caloi", 99)


def test_quem_usa_nao_percebe_a_property():
    # Para quem usa, continua parecendo um atributo comum.
    b = Bicicleta("Caloi")
    b.marcha_atual = 3
    b.pedalar()
    assert b.velocidade == 3
