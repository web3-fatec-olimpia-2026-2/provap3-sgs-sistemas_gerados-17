"""Testes da Reserva (Aula 02). Na ordem do TDD: criar → barrar inválido → calcular."""
import pytest

from reserva import Reserva


def test_cria_reserva():
    r = Reserva("Ana", 101, 3, 250)
    assert r.valor_diaria == 250
    assert r.diarias == 3


def test_valor_negativo_da_erro_ao_alterar():
    r = Reserva("Ana", 101, 3, 250)
    with pytest.raises(ValueError):
        r.valor_diaria = -100


def test_valor_negativo_da_erro_ja_na_criacao():
    # Prova que o __init__ passa pelo setter.
    with pytest.raises(ValueError):
        Reserva("Ana", 101, 3, -1)


def test_diarias_zero_da_erro():
    r = Reserva("Ana", 101, 3, 250)
    with pytest.raises(ValueError):
        r.diarias = 0


def test_uma_diaria_e_valida():
    # Teste de LIMITE: pega o bug "<= 1" do repositório de referência.
    r = Reserva("Ana", 101, 1, 250)
    assert r.total == 250


def test_valor_zero_e_valido():
    # Limite do outro lado: cortesia (diária 0) não é negativa, então é aceita.
    assert Reserva("Ana", 101, 2, 0).total == 0


def test_total_calcula():
    assert Reserva("Ana", 101, 4, 200).total == 800


def test_total_acompanha_mudanca():
    r = Reserva("Ana", 101, 4, 200)
    r.diarias = 5
    assert r.total == 1000
    r.valor_diaria = 250
    assert r.total == 1250


def test_total_e_somente_leitura():
    r = Reserva("Ana", 101, 4, 200)
    with pytest.raises(AttributeError):
        r.total = 1   # property sem setter não aceita escrita
