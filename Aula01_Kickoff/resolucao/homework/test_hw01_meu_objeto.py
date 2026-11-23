"""Testes do Homework 01: provam que o estado pertence a cada objeto."""
import pytest

from hw01_meu_objeto import Bicicleta


def test_bicicleta_nasce_parada_na_primeira_marcha():
    b = Bicicleta("Caloi")
    assert b.velocidade == 0
    assert b.marcha_atual == 1


def test_pedalar_em_marcha_maior_acelera_mais():
    b = Bicicleta("Caloi")
    b.trocar_marcha(5)
    b.pedalar()
    assert b.velocidade == 5


def test_frear_reduz_pela_metade():
    b = Bicicleta("Caloi")
    b.trocar_marcha(4)
    b.pedalar()      # 4
    b.pedalar()      # 8
    b.frear()        # 4
    assert b.velocidade == 4


def test_marcha_invalida_e_recusada():
    b = Bicicleta("Caloi")
    with pytest.raises(ValueError):
        b.trocar_marcha(0)
    with pytest.raises(ValueError):
        b.trocar_marcha(22)


def test_dois_objetos_nao_compartilham_estado():
    # O ponto crítico do slide 25: chamar o método em um objeto não altera o outro.
    a, b = Bicicleta("A"), Bicicleta("B")
    a.pedalar()
    assert a.velocidade == 1
    assert b.velocidade == 0
