"""Testes do PROTOTYPE: clone independente, profundo e validado; o registro entrega cópias."""
import pytest

from destinos.nucleo.antes_prototipos import copiar_na_mao
from destinos.nucleo.prototipos import RegistroDePrototipos, clonar
from destinos.tests.nucleo.fabrica import criar


def test_clone_e_outro_objeto_com_os_mesmos_dados():
    original = criar()
    copia = clonar(original)
    assert copia is not original and vars(copia) == vars(original)


def test_mudar_o_clone_nao_muda_o_original():
    original = criar()
    copia = clonar(original, quantidade=original.quantidade + 1)
    assert copia.quantidade == original.quantidade + 1 and vars(original) == vars(criar())


def test_mudanca_invalida_e_barrada():
    with pytest.raises(ValueError):
        clonar(criar(), quantidade=0)


def test_campo_inexistente_e_recusado():
    with pytest.raises(AttributeError):
        clonar(criar(), campo_que_nao_existe=1)


def test_copia_profunda_nao_compartilha_listas():
    original = criar()
    original.etiquetas = ["original"]  # dado novo, que a Destino não conhecia
    copia = clonar(original)
    copia.etiquetas.append("so na copia")
    assert original.etiquetas == ["original"]


def test_copia_na_mao_esquece_o_dado_novo():
    original = criar()
    original.etiquetas = ["original"]
    assert copiar_na_mao(original).total == original.total
    assert not hasattr(copiar_na_mao(original), "etiquetas")
    assert clonar(original).etiquetas == ["original"]


def test_registro_entrega_clones_do_modelo():
    registro = RegistroDePrototipos()
    registro.registrar("padrao", criar())
    a = registro.criar("padrao")
    b = registro.criar("padrao", cliente="Bruno")
    assert a is not b and b.cliente == "Bruno" and registro.nomes() == ["padrao"]


def test_modelo_desconhecido():
    with pytest.raises(KeyError):
        RegistroDePrototipos().criar("nao existe")
