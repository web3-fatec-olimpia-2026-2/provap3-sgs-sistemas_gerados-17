"""Testes do MEMENTO: salvar, restaurar várias versões e não expor o interior."""
import pytest

from nucleo.antes_versoes import restaurar_antigo, salvar_antigo
from nucleo.versoes import EditorReserva, HistoricoDeVersoes
from tests.fabrica import criar


def test_restaurar_volta_ao_estado_salvo():
    item = criar()
    editor = EditorReserva(item)
    versao = editor.salvar("original")
    editor.alterar("diarias", item.diarias + 1)
    editor.restaurar(versao)
    assert vars(item) == vars(criar())


def test_memento_e_uma_copia():
    item = criar()
    versao = EditorReserva(item).salvar()
    item.diarias = item.diarias + 1
    assert versao._estado != vars(item)


def test_historico_volta_varias_versoes():
    item = criar()
    editor, historico = EditorReserva(item), HistoricoDeVersoes()
    q0 = item.diarias
    for passo in (1, 2):
        historico.guardar(editor.salvar(f"antes do passo {passo}"))
        editor.alterar("diarias", q0 + passo)
    assert historico.rotulos() == ["antes do passo 1", "antes do passo 2"]
    editor.restaurar(historico.ultima())
    assert item.diarias == q0 + 1
    editor.restaurar(historico.ultima())
    assert item.diarias == q0
    assert historico.ultima() is None


def test_alteracao_invalida_continua_barrada():
    with pytest.raises(ValueError):
        EditorReserva(criar()).alterar("diarias", 0)


def test_mesmo_resultado_da_copia_na_mao():
    a, b = criar(), criar()
    copia = salvar_antigo(a)
    versao = EditorReserva(b).salvar()
    a.diarias = a.diarias + 1
    b.diarias = b.diarias + 1
    restaurar_antigo(a, copia)
    EditorReserva(b).restaurar(versao)
    assert vars(a) == vars(b)
