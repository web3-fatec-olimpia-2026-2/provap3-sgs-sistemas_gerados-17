"""Testes do POLIMORFISMO: mesma saída que o if/elif, e categoria nova sem mudar a função."""
import pytest

from nucleo import antes_categorias
from nucleo.categorias import Basico, BasicoPadrao, Intermediario, Personalizado, Premium, imprimir_preco


@pytest.mark.parametrize("classe, tipo", [(Intermediario, "intermediario"), (Premium, "premium")])
def test_mesmo_texto_que_a_versao_com_if(classe, tipo):
    assert imprimir_preco(classe(1)) == antes_categorias.imprimir_preco(tipo)


def test_base_igual_ao_else_da_versao_antiga():
    assert imprimir_preco(Basico(1)) == antes_categorias.imprimir_preco("qualquer")


@pytest.mark.parametrize("classe", [Intermediario, Premium, Personalizado, BasicoPadrao])
def test_todo_subtipo_e_um_basico(classe):
    assert isinstance(classe(1), Basico)


def test_subtipo_herda_o_construtor():
    assert Intermediario(7).codigo == 7


def test_categoria_nova_sem_mudar_a_funcao():
    assert imprimir_preco(Personalizado(1)) == "Personalizado: R$ 300.00 por unidade"


def test_quem_nao_sobrescreve_usa_o_metodo_da_mae():
    assert imprimir_preco(BasicoPadrao(1)) == imprimir_preco(Basico(1))


def test_versao_com_if_erra_a_categoria_nova():
    assert antes_categorias.imprimir_preco("personalizado") != imprimir_preco(Personalizado(1))
