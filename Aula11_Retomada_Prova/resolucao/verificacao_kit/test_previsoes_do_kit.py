"""Confere, rodando, as respostas das Partes 2 e 3 do Kit de Revisão."""
from pecas_do_kit import (ComCafeDaManha, ComCafeDaManhaComErro, ComTransfer,
                          Reserva, ReservaBase, TarifaParceiro)


def test_parte_2_1_decorators_empilhados():
    r = ComTransfer(ComCafeDaManha(ReservaBase(200, 2)))
    assert r.preco() == 520.0                       # 400 + 40 + 80


def test_parte_2_1_ordem_nao_muda():
    a = ComTransfer(ComCafeDaManha(ReservaBase(200, 2)))
    b = ComCafeDaManha(ComTransfer(ReservaBase(200, 2)))
    assert a.preco() == b.preco()


def test_parte_2_2_strategy():
    assert Reserva(500, TarifaParceiro()).total() == 400.0


def test_parte_3_1_decorador_sem_somar_so_delega():
    errado = ComCafeDaManhaComErro(ReservaBase(200, 2))
    certo = ComCafeDaManha(ReservaBase(200, 2))
    assert errado.preco() == 400        # o bug: não somou o café
    assert certo.preco() == 440.0       # corrigido


def test_verificacao_de_saida_do_material():
    # "ComCafe(ReservaBase(200,2)).preco() devolveu 200" → o certo seria 440.
    # (no enunciado do material a base era 1 noite: 200 → 240)
    assert ComCafeDaManha(ReservaBase(200, 1)).preco() == 240.0
