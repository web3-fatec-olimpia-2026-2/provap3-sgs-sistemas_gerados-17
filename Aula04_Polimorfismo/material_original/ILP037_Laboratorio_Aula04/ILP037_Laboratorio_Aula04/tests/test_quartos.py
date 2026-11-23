import pytest
from quartos import Quarto, Suite, Presidencial, imprimir_diaria

# --- Quarto base: JA PASSA ---
def test_quarto_comum():
    q = Quarto(101)
    assert q.descricao() == "Quarto comum"
    assert q.preco_noite() == 200

# --- Suite: SUA TAREFA ---
def test_suite_sobrescreve():
    s = Suite(201)
    assert s.descricao() == "Suite"
    assert s.preco_noite() == 500

def test_suite_e_um_quarto():
    s = Suite(201)
    assert isinstance(s, Quarto)      # herda: Suite E-UM Quarto

# --- Presidencial: SUA TAREFA ---
def test_presidencial_sobrescreve():
    p = Presidencial(301)
    assert p.descricao() == "Quarto presidencial"
    assert p.preco_noite() == 1200

# --- POLIMORFISMO: a mesma funcao trata os tres ---
def test_funcao_polimorfica():
    assert imprimir_diaria(Quarto(1)) == "Quarto comum: R$ 200"
    assert imprimir_diaria(Suite(2)) == "Suite: R$ 500"
    assert imprimir_diaria(Presidencial(3)) == "Quarto presidencial: R$ 1200"
