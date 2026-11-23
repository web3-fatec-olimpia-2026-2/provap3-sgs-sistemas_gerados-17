"""Aula 04 — os 5 testes ORIGINAIS do laboratório + os meus (desafio e contraste com if)."""
from quartos import (Chale, Presidencial, Quarto, QuartoStandard, Suite,
                     imprimir_diaria, imprimir_diaria_com_if)


# --- originais ---
def test_quarto_comum():
    q = Quarto(101)
    assert q.descricao() == "Quarto comum"
    assert q.preco_noite() == 200


def test_suite_sobrescreve():
    s = Suite(201)
    assert s.descricao() == "Suite"
    assert s.preco_noite() == 500


def test_suite_e_um_quarto():
    assert isinstance(Suite(201), Quarto)


def test_presidencial_sobrescreve():
    p = Presidencial(301)
    assert p.descricao() == "Quarto presidencial"
    assert p.preco_noite() == 1200


def test_funcao_polimorfica():
    assert imprimir_diaria(Quarto(1)) == "Quarto comum: R$ 200"
    assert imprimir_diaria(Suite(2)) == "Suite: R$ 500"
    assert imprimir_diaria(Presidencial(3)) == "Quarto presidencial: R$ 1200"


# --- meus ---
def test_chale_funciona_sem_mudar_a_funcao():
    # "Aberto ao novo": classe nova, função intacta.
    assert imprimir_diaria(Chale(4)) == "Chale: R$ 350"


def test_subtipo_que_nao_sobrescreve_usa_o_da_mae():
    assert imprimir_diaria(QuartoStandard(5)) == "Quarto comum: R$ 200"


def test_herdou_o_construtor():
    assert Presidencial(301).numero == 301


def test_versao_com_if_erra_o_tipo_novo():
    # Mostra o risco do if/elif: o Chalé cai no "else" e recebe o preço errado.
    assert imprimir_diaria_com_if(Chale(4)) != imprimir_diaria(Chale(4))
