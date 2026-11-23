"""Testes do POLIMORFISMO: mesma saída que o if/elif, e categoria nova sem mudar a função."""
import pytest

from nucleo.categorias import Basico, BasicoPadrao, Intermediario, Personalizado, Premium, imprimir_preco


@pytest.mark.parametrize("classe", [Intermediario, Premium, Personalizado, BasicoPadrao])
def test_todo_subtipo_e_um_basico(classe):
    assert isinstance(classe(1), Basico)


def test_subtipo_herda_o_construtor():
    assert Intermediario(7).codigo == 7


def test_categoria_nova_sem_mudar_a_funcao():
    assert imprimir_preco(Personalizado(1)) == "Personalizado: R$ 300.00 por unidade"


def test_quem_nao_sobrescreve_usa_o_metodo_da_mae():
    assert imprimir_preco(BasicoPadrao(1)) == imprimir_preco(Basico(1))
