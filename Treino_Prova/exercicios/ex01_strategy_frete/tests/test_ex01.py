"""Testes do ex01. Por padrão rodam no gabarito; ALVO=exercicio testa a sua resolução."""
import importlib
import os

import pytest

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))

ESTRATEGIAS = [("pac", m.FretePAC), ("sedex", m.FreteSedex), ("retirada", m.RetiradaNaLoja)]


@pytest.mark.parametrize("tipo, classe", ESTRATEGIAS)
@pytest.mark.parametrize("peso", [0, 1, 2.5, 10])
def test_mesmo_valor_que_o_if_elif(tipo, classe, peso):
    assert m.Pedido(peso, classe()).frete() == m.PedidoAntigo(peso, tipo).frete()


def test_motoboy_sem_mexer_no_pedido():
    assert m.Pedido(5, m.FreteMotoboy()).frete() == 15


def test_motoboy_acima_do_limite():
    with pytest.raises(ValueError):
        m.Pedido(5.1, m.FreteMotoboy()).frete()


def test_pedido_nao_tem_if_de_tipo():
    # Qualquer objeto com calcular() serve — prova de que o Pedido só conhece a interface.
    class FreteDrone:
        def calcular(self, peso_kg):
            return 50

    assert m.Pedido(1, FreteDrone()).frete() == 50
