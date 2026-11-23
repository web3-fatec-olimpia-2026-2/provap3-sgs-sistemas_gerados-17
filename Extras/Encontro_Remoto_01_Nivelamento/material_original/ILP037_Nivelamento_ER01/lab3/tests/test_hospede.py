import pytest
from hospede import Hospede, HospedeVIP

def test_vip_e_um_hospede():
    v = HospedeVIP("Ana", "123", 30, 500)
    assert isinstance(v, Hospede)      # o VIP E-UM Hospede

def test_vip_herda_nome_e_documento():
    v = HospedeVIP("Ana", "123", 30, 500)
    assert v.nome == "Ana"
    assert v.documento == "123"

def test_vip_herda_check_in():
    v = HospedeVIP("Ana", "123", 30, 500)
    v.fazer_check_in()                 # metodo herdado do Hospede
    assert v.hospedado == True

def test_vip_tem_pontos():
    v = HospedeVIP("Ana", "123", 30, 500)
    assert v.pontos == 500

def test_vip_herda_protecao_da_idade():
    # a protecao da idade tambem e herdada
    v = HospedeVIP("Ana", "123", 30, 500)
    with pytest.raises(ValueError):
        v.idade = -1
