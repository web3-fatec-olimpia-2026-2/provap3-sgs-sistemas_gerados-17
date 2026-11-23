import pytest

from nucleo.versoes import EditorIngresso, HistoricoDeVersoes
from tests.fabrica import criar


def test_restaurar_volta_ao_estado_salvo():
    item = criar()
    editor = EditorIngresso(item)
    versao = editor.salvar("original")
    editor.alterar("quantidade", item.quantidade + 1)
    editor.restaurar(versao)
    assert vars(item) == vars(criar())


def test_memento_e_uma_copia():
    item = criar()
    versao = EditorIngresso(item).salvar()
    item.quantidade = item.quantidade + 1
    assert versao._estado != vars(item)


def test_historico_volta_varias_versoes():
    item = criar()
    editor, historico = EditorIngresso(item), HistoricoDeVersoes()
    q0 = item.quantidade
    for passo in (1, 2):
        historico.guardar(editor.salvar(f"antes do passo {passo}"))
        editor.alterar("quantidade", q0 + passo)
    assert historico.rotulos() == ["antes do passo 1", "antes do passo 2"]
    editor.restaurar(historico.ultima())
    assert item.quantidade == q0 + 1
    editor.restaurar(historico.ultima())
    assert item.quantidade == q0
    assert historico.ultima() is None


def test_alteracao_invalida_continua_barrada():
    with pytest.raises(ValueError):
        EditorIngresso(criar()).alterar("quantidade", 0)
