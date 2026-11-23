"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.extras import Adicional, AtendimentoBase, ComDesconto10, ComEmbalagem, ComSeguro, ComUrgente
from tests.fabrica import criar

FLAGS = {ComUrgente: "urgente", ComEmbalagem: "embalagem", ComSeguro: "seguro"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


def test_componente_entrega_o_total():
    item = criar()
    assert AtendimentoBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(AtendimentoBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComEmbalagem(ComUrgente(AtendimentoBase(item)))
    base = f"Atendimento de {item.cliente} ({item.quantidade} unidade(s))"
    assert componente.descricao() == base + " + urgente" + " + embalagem"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComUrgente(ComUrgente(AtendimentoBase(item))).preco() == pytest.approx(item.total + 2 * 30.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComDesconto10(ComUrgente(AtendimentoBase(item)))
    por_dentro = ComUrgente(ComDesconto10(AtendimentoBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 30.0) * 0.9, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 0.9, 2) + 30.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComUrgente, ComEmbalagem, ComSeguro, ComDesconto10])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(AtendimentoBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
