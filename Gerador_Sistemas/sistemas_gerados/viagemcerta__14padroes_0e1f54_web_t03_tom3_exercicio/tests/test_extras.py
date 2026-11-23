"""Testes do DECORATOR: mesma conta das flags, empilhamento e ordem com camada que multiplica."""
import itertools

import pytest

from nucleo.antes_extras import preco_com_flags
from nucleo.extras import Adicional, ViagcertBase, ComAltaTemporada, ComPasseioGuiado, ComSeguroViagem, ComTranslado
from tests.fabrica import criar

FLAGS = {ComSeguroViagem: "seguro_viagem", ComTranslado: "translado", ComPasseioGuiado: "passeio_guiado"}
COMBINACOES = [c for n in range(len(FLAGS) + 1) for c in itertools.combinations(FLAGS, n)]


@pytest.mark.parametrize("combinacao", COMBINACOES)
def test_qualquer_combinacao_bate_com_as_flags(combinacao):
    item = criar()
    componente = ViagcertBase(item)
    for extra in combinacao:
        componente = extra(componente)
    esperado = preco_com_flags(item, **{FLAGS[e]: True for e in combinacao})
    assert componente.preco() == pytest.approx(esperado)


def test_componente_entrega_o_total():
    item = criar()
    assert ViagcertBase(item).preco() == item.total


def test_decorador_base_so_delega():
    item = criar()
    assert Adicional(ViagcertBase(item)).preco() == item.total


def test_descricao_segue_a_ordem_do_embrulho():
    item = criar()
    componente = ComTranslado(ComSeguroViagem(ViagcertBase(item)))
    base = f"Viagcert de {item.viajante} ({item.noites} noite(s))"
    assert componente.descricao() == base + " + seguro viagem" + " + translado"


def test_mesmo_extra_duas_vezes():
    item = criar()
    assert ComSeguroViagem(ComSeguroViagem(ViagcertBase(item))).preco() == pytest.approx(item.total + 2 * 90.0)


def test_com_camada_que_multiplica_a_ordem_importa():
    item = criar()
    base = item.total
    por_fora = ComAltaTemporada(ComSeguroViagem(ViagcertBase(item)))
    por_dentro = ComSeguroViagem(ComAltaTemporada(ViagcertBase(item)))
    assert por_fora.preco() == pytest.approx(round((base + 90.0) * 1.25, 2))
    assert por_dentro.preco() == pytest.approx(round(round(base * 1.25, 2) + 90.0, 2))
    assert por_fora.preco() != por_dentro.preco()


@pytest.mark.parametrize("classe", [Adicional, ComSeguroViagem, ComTranslado, ComPasseioGuiado, ComAltaTemporada])
def test_todo_decorador_mantem_a_interface(classe):
    embrulho = classe(ViagcertBase(criar()))
    assert callable(embrulho.preco) and callable(embrulho.descricao)
