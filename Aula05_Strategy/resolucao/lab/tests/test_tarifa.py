"""Aula 05 — testes após a refatoração.

Regra de ouro da refatoração: os RESULTADOS não podem mudar (400, 360, 320).
Mudou só a forma de chamar: passa-se um objeto-estratégia em vez de um texto.
"""
import pytest

import tarifa_antes
from tarifa import (Reserva, ReservaComFuncao, TarifaComum, TarifaFidelidade,
                    TarifaParceiro, TarifaVIP, tarifa_estudante)


# --- os 3 testes do laboratório, na nova assinatura ---
def test_comum():
    assert Reserva(2, 200, TarifaComum()).total() == 400


def test_fidelidade():
    assert Reserva(2, 200, TarifaFidelidade()).total() == 360.0


def test_parceiro():
    assert Reserva(2, 200, TarifaParceiro()).total() == 320.0


# --- Passo 4: aberto ao novo ---
def test_aberto_ao_novo():
    # VIP definida aqui mesmo, no teste: prova que a Reserva nem precisou saber dela.
    class TarifaVIPLocal:
        def aplicar(self, base):
            return base * 0.50

    assert Reserva(2, 200, TarifaVIPLocal()).total() == 200.0
    assert Reserva(2, 200, TarifaVIP()).total() == 200.0


# --- meus: rede de segurança "antes × depois" ---
@pytest.mark.parametrize("texto, estrategia", [
    ("comum", TarifaComum()),
    ("fidelidade", TarifaFidelidade()),
    ("parceiro", TarifaParceiro()),
])
@pytest.mark.parametrize("diarias, valor", [(1, 100), (2, 200), (7, 315.5)])
def test_refatoracao_preserva_o_comportamento(texto, estrategia, diarias, valor):
    antes = tarifa_antes.Reserva(diarias, valor, texto).total()
    depois = Reserva(diarias, valor, estrategia).total()
    assert depois == antes


def test_estrategia_pode_ser_trocada_em_tempo_de_execucao():
    r = Reserva(2, 200, TarifaComum())
    assert r.total() == 400
    r.tarifa = TarifaParceiro()          # hóspede virou parceiro
    assert r.total() == 320.0


def test_estrategia_como_funcao():
    assert ReservaComFuncao(2, 200, tarifa_estudante).total() == 340.0
    assert ReservaComFuncao(2, 200, lambda base: base).total() == 400
