"""Testes do POLIMORFISMO: mesma saída que o if/elif, e categoria nova sem mudar a função."""
import pytest

from nucleo import antes_categorias
from nucleo.categorias import LaranjaPera, LaranjaPeraPadrao, LaranjaValencia, LimaoTahiti, TangerinaPonkan, imprimir_preco


@pytest.mark.parametrize("classe, tipo", [(LaranjaValencia, "laranja_valencia"), (LimaoTahiti, "limao_tahiti")])
def test_mesmo_texto_que_a_versao_com_if(classe, tipo):
    assert imprimir_preco(classe(1)) == antes_categorias.imprimir_preco(tipo)


def test_base_igual_ao_else_da_versao_antiga():
    assert imprimir_preco(LaranjaPera(1)) == antes_categorias.imprimir_preco("qualquer")


@pytest.mark.parametrize("classe", [LaranjaValencia, LimaoTahiti, TangerinaPonkan, LaranjaPeraPadrao])
def test_todo_subtipo_e_um_laranja_pera(classe):
    assert isinstance(classe(1), LaranjaPera)


def test_subtipo_herda_o_construtor():
    assert LaranjaValencia(7).codigo == 7


def test_categoria_nova_sem_mudar_a_funcao():
    assert imprimir_preco(TangerinaPonkan(1)) == "Tangerina Ponkan: R$ 52.00 por caixa"


def test_quem_nao_sobrescreve_usa_o_metodo_da_mae():
    assert imprimir_preco(LaranjaPeraPadrao(1)) == imprimir_preco(LaranjaPera(1))


def test_versao_com_if_erra_a_categoria_nova():
    assert antes_categorias.imprimir_preco("tangerina_ponkan") != imprimir_preco(TangerinaPonkan(1))
