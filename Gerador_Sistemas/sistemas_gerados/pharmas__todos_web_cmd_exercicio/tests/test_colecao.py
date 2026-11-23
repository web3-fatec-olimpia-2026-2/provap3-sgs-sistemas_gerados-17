"""Testes do ITERATOR: for/list/sum funcionam, percursos independentes, filtrado e ordenado."""
import pytest

from nucleo.antes_colecao import ColecaoAntiga, totais_antigo
from nucleo.colecao import ColecaoPharm, IteradorDeItens
from tests.fabrica import itens_exemplo


def cheia():
    colecao = ColecaoPharm()
    for item in itens_exemplo():
        colecao.adicionar(item)
    return colecao


def test_for_percorre_na_ordem_de_entrada():
    assert [item.cliente for item in cheia()] == [item.cliente for item in itens_exemplo()]


def test_mesmos_totais_que_o_laco_por_indice():
    antiga = ColecaoAntiga()
    for item in itens_exemplo():
        antiga.adicionar(item)
    assert [item.total for item in cheia()] == totais_antigo(antiga)


def test_iterador_avisa_o_fim():
    with pytest.raises(StopIteration):
        next(IteradorDeItens([]))


def test_dois_percursos_independentes():
    colecao = cheia()
    a, b = iter(colecao), iter(colecao)
    next(a)
    assert next(b).cliente == itens_exemplo()[0].cliente


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
    assert [item.cliente for item in colecao] == [item.cliente for item in itens_exemplo()]


def test_funciona_com_as_funcoes_do_python():
    colecao = cheia()
    assert len(colecao) == 4
    assert round(sum(item.total for item in colecao), 2) == round(sum(i.total for i in itens_exemplo()), 2)
