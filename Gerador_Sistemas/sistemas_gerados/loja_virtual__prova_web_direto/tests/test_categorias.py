"""Testes do POLIMORFISMO: mesma saída que o if/elif, e categoria nova sem mudar a função."""
import pytest

from nucleo.categorias import Alimento, Eletronico, Livro, Produto, ProdutoPadrao, imprimir_preco


@pytest.mark.parametrize("classe", [Eletronico, Livro, Alimento, ProdutoPadrao])
def test_todo_subtipo_e_um_produto(classe):
    assert isinstance(classe(1), Produto)


def test_subtipo_herda_o_construtor():
    assert Eletronico(7).codigo == 7


def test_categoria_nova_sem_mudar_a_funcao():
    assert imprimir_preco(Alimento(1)) == "Alimento: R$ 20.00 por unidade"


def test_quem_nao_sobrescreve_usa_o_metodo_da_mae():
    assert imprimir_preco(ProdutoPadrao(1)) == imprimir_preco(Produto(1))
