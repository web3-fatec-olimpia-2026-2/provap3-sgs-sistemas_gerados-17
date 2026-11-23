"""
ILP-037 Aula 03 - Testes do laboratorio.

Estes testes sao a sua REDE DE SEGURANCA e a sua ESPECIFICACAO:
eles dizem, em codigo, o que o seu Quarto precisa fazer.

Rode com:   python3 -m pytest tests/ -v

NO COMECO: 2 passam (diaria, que ja vem pronta) e 2 falham
(capacidade, que e a sua tarefa). Isso e o CERTO - o vermelho
e a sua lista de tarefas.

NO FINAL: os 4 verdes. Ai voce terminou.

NAO ALTERE ESTE ARQUIVO. Ele e o alvo; quem se move e o quarto.py.
"""

import pytest
from quarto import Quarto


# --- diaria: JA PASSA (a classe ja vem com isto pronto) ----------------

def test_cria_quarto_com_diaria():
    q = Quarto(101, 250, 2)
    assert q.diaria == 250


def test_diaria_negativa_levanta_erro():
    q = Quarto(101, 250, 2)
    with pytest.raises(ValueError):
        q.diaria = -30


# --- capacidade: SUA TAREFA (comecam VERMELHOS) ------------------------

def test_cria_quarto_com_capacidade():
    q = Quarto(101, 250, 2)
    assert q.capacidade == 2


def test_capacidade_zero_levanta_erro():
    q = Quarto(101, 250, 2)
    with pytest.raises(ValueError):
        q.capacidade = 0
