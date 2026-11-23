"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.antes_extras import preco_com_flags
from nucleo.extras import Adicional, PharmBase, ComDesconto10, ComEmbalagem, ComSeguro, ComUrgente
from tests.fabrica import criar

FLAGS = {ComUrgente: "urgente", ComEmbalagem: "embalagem", ComSeguro: "seguro"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


@pytest.mark.parametrize("combinacao", COMBINACOES)
def test_qualquer_combinacao_bate_com_as_flags(combinacao):
    item = criar()
    componente = PharmBase(item)
    for extra in combinacao:
        componente = extra(componente)
    esperado = preco_com_flags(item, **{FLAGS[e]: True for e in combinacao})
    assert componente.preco() == pytest.approx(esperado)


def test_componente_entrega_o_total():
    item = criar()
    assert PharmBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(PharmBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComEmbalagem(ComUrgente(PharmBase(item)))
    base = f"Pharm de {item.cliente} ({item.quantidade} unidade(s))"
    assert componente.descricao() == base + " + urgente" + " + embalagem"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComUrgente(ComUrgente(PharmBase(item))).preco() == pytest.approx(item.total + 2 * 30.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComDesconto10(ComUrgente(PharmBase(item)))
    por_dentro = ComUrgente(ComDesconto10(PharmBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 30.0) * 0.9, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 0.9, 2) + 30.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComUrgente, ComEmbalagem, ComSeguro, ComDesconto10])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(PharmBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
