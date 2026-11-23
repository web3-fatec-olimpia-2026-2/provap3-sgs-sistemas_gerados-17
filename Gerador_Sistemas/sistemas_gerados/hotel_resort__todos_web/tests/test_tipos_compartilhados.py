"""Testes do FLYWEIGHT: mesma chave → mesmo objeto; mil registros, poucos flyweights."""
import pytest

from nucleo.antes_tipos_compartilhados import registrar_antigo, valor_antigo
from nucleo.tipos_compartilhados import TIPOS, FabricaDeTipos, Registro
from tests.fabrica import itens_exemplo

CHAVES = sorted(TIPOS)


def test_mesma_chave_mesmo_objeto():
    fabrica = FabricaDeTipos()
    assert fabrica.obter(CHAVES[0]) is fabrica.obter(CHAVES[0])


def test_mil_registros_poucos_flyweights():
    fabrica = FabricaDeTipos()
    itens = itens_exemplo()
    registros = [Registro(itens[i % 4], fabrica.obter(CHAVES[i % len(CHAVES)])) for i in range(1000)]
    assert len(registros) == 1000 and fabrica.quantidade() == len(CHAVES)


def test_antes_cria_um_objeto_por_registro():
    item = itens_exemplo()[0]
    assert registrar_antigo(item, CHAVES[0])[1] is not registrar_antigo(item, CHAVES[0])[1]


@pytest.mark.parametrize("chave", CHAVES)
@pytest.mark.parametrize("indice", range(4))
def test_mesmo_valor_que_a_versao_antiga(chave, indice):
    item = itens_exemplo()[indice]
    assert Registro(item, FabricaDeTipos().obter(chave)).valor() == valor_antigo(registrar_antigo(item, chave))


def test_flyweight_e_imutavel():
    tipo = FabricaDeTipos().obter(CHAVES[0])
    with pytest.raises(AttributeError):
        tipo.fator = 0


def test_chave_desconhecida():
    with pytest.raises(KeyError):
        FabricaDeTipos().obter("nao_existe")
