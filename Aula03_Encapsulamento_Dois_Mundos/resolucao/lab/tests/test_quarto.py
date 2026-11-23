"""
Aula 03 — testes. Os 4 primeiros são os ORIGINAIS do laboratório (não alterados);
os demais são meus, cobrindo limites, o desafio e a herança.

Rodar (dentro de resolucao/lab):  python3 -m pytest tests/ -v
"""
import pytest

from quarto import Frigobar, Quarto, QuartoComFrigobar, Suite


# --- originais do laboratório -------------------------------------------
def test_cria_quarto_com_diaria():
    q = Quarto(101, 250, 2)
    assert q.diaria == 250


def test_diaria_negativa_levanta_erro():
    q = Quarto(101, 250, 2)
    with pytest.raises(ValueError):
        q.diaria = -30


def test_cria_quarto_com_capacidade():
    q = Quarto(101, 250, 2)
    assert q.capacidade == 2


def test_capacidade_zero_levanta_erro():
    q = Quarto(101, 250, 2)
    with pytest.raises(ValueError):
        q.capacidade = 0


# --- meus: limites -------------------------------------------------------
def test_capacidade_um_e_valida():
    assert Quarto(101, 250, 1).capacidade == 1


def test_capacidade_invalida_barrada_na_criacao():
    with pytest.raises(ValueError):
        Quarto(101, 250, 0)


def test_diaria_zero_e_valida():
    # diferença de regra: diária barra < 0; capacidade barra < 1
    assert Quarto(101, 0, 2).diaria == 0


# --- meus: desafio -------------------------------------------------------
def test_receita_maxima():
    q = Quarto(101, 250, 2)
    assert q.receita_maxima == 500


def test_receita_maxima_acompanha_mudanca():
    q = Quarto(101, 250, 2)
    q.capacidade = 4
    assert q.receita_maxima == 1000


def test_receita_maxima_e_somente_leitura():
    q = Quarto(101, 250, 2)
    with pytest.raises(AttributeError):
        q.receita_maxima = 1


# --- meus: herança e composição -----------------------------------------
def test_suite_e_um_quarto_e_herda_validacao():
    s = Suite(201, 600, 3)
    assert isinstance(s, Quarto)          # É-UM
    assert s.tem_sala is True
    with pytest.raises(ValueError):       # a validação veio de graça pelo super()
        s.capacidade = 0


def test_quarto_tem_um_frigobar():
    q = QuartoComFrigobar(102, 250, 2)
    assert isinstance(q.frigobar, Frigobar)   # TEM-UM
    assert not isinstance(q, Frigobar)        # mas não É um frigobar
