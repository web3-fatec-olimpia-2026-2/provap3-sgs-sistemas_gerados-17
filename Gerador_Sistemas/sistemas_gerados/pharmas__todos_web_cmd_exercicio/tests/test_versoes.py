"""Testes do MEMENTO: salvar, restaurar várias versões e não expor o interior."""
import pytest

from nucleo.antes_versoes import restaurar_antigo, salvar_antigo
from nucleo.versoes import EditorPharm, HistoricoDeVersoes
from tests.fabrica import criar


def test_restaurar_volta_ao_estado_salvo():
    item = criar()
    editor = EditorPharm(item)
    versao = editor.salvar("original")
    editor.alterar("quantidade", item.quantidade + 1)
    editor.restaurar(versao)
    assert vars(item) == vars(criar())


def test_memento_e_uma_copia():
    item = criar()
    versao = EditorPharm(item).salvar()
    item.quantidade = item.quantidade + 1
    assert versao._estado != vars(item)


def test_historico_volta_varias_versoes():
    item = criar()
    editor, historico = EditorPharm(item), HistoricoDeVersoes()
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
        EditorPharm(criar()).alterar("quantidade", 0)


def test_mesmo_resultado_da_copia_na_mao():
    a, b = criar(), criar()
    copia = salvar_antigo(a)
    versao = EditorPharm(b).salvar()
    a.quantidade = a.quantidade + 1
    b.quantidade = b.quantidade + 1
    restaurar_antigo(a, copia)
    EditorPharm(b).restaurar(versao)
    assert vars(a) == vars(b)
