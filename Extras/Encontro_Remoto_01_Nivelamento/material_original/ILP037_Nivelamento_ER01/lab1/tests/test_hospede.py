import pytest
from hospede import Hospede

def test_cria_hospede():
    h = Hospede("Ana", "123")
    assert h.nome == "Ana"
    assert h.documento == "123"

def test_hospede_comeca_sem_checkin():
    h = Hospede("Ana", "123")
    assert h.hospedado == False

def test_fazer_check_in():
    h = Hospede("Ana", "123")
    h.fazer_check_in()
    assert h.hospedado == True

def test_dois_hospedes_sao_independentes():
    ana = Hospede("Ana", "123")
    bruno = Hospede("Bruno", "456")
    ana.fazer_check_in()
    assert ana.hospedado == True
    assert bruno.hospedado == False
