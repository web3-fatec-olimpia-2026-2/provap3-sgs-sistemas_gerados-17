import pytest

from nucleo.colecao import ColecaoIngresso, IteradorDeItens
from tests.fabrica import itens_exemplo


def cheia():
    colecao = ColecaoIngresso()
    for item in itens_exemplo():
        colecao.adicionar(item)
    return colecao


def test_for_percorre_na_ordem_de_entrada():
    assert [item.espectador for item in cheia()] == [item.espectador for item in itens_exemplo()]


def test_iterador_avisa_o_fim():
    with pytest.raises(StopIteration):
        next(IteradorDeItens([]))


def test_dois_percursos_independentes():
    colecao = cheia()
    a, b = iter(colecao), iter(colecao)
    next(a)
    assert next(b).espectador == itens_exemplo()[0].espectador


def test_percurso_filtrado():
    colecao = cheia()
    limite = sorted(item.total for item in colecao)[1]
    filtrados = list(colecao.acima_de(limite))
    assert all(item.total > limite for item in filtrados)
    assert len(filtrados) == sum(1 for item in colecao if item.total > limite)


def test_percurso_ordenado_nao_muda_a_colecao():
    colecao = cheia()
    totais = [item.total for item in colecao.ordenados_por_total()]
    assert totais == sorted(totais)
    assert [item.espectador for item in colecao] == [item.espectador for item in itens_exemplo()]


def test_funciona_com_as_funcoes_do_python():
    colecao = cheia()
    assert len(colecao) == 4
    assert round(sum(item.total for item in colecao), 2) == round(sum(i.total for i in itens_exemplo()), 2)
