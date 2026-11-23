import pytest
from hospede import Hospede

def test_cria_hospede_com_idade():
    h = Hospede("Ana", "123", 30)
    assert h.idade == 30

def test_check_in_continua_funcionando():
    h = Hospede("Ana", "123", 30)
    h.fazer_check_in()
    assert h.hospedado == True

def test_idade_negativa_levanta_erro():
    h = Hospede("Ana", "123", 30)
    with pytest.raises(ValueError):
        h.idade = -5

def test_idade_zero_e_valida():
    # um bebe de colo tem idade 0 - e valido
    h = Hospede("Bebe", "000", 0)
    assert h.idade == 0
