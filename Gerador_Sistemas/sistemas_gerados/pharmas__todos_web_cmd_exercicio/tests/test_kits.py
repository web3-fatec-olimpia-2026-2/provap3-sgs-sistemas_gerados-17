"""Testes do ABSTRACT FACTORY: relatórios idênticos à versão antiga e famílias que não se misturam."""
import pytest

from nucleo.antes_kits import montar_relatorio_antigo
from nucleo.kits import KitHtml, KitMarkdown, KitRelatorio, KitTexto, montar_relatorio
from tests.fabrica import itens_exemplo


@pytest.mark.parametrize("formato, kit", [("texto", KitTexto), ("html", KitHtml)])
def test_refatoracao_preserva_o_relatorio(formato, kit):
    itens = itens_exemplo()
    assert montar_relatorio(kit(), itens) == montar_relatorio_antigo(itens, formato)


def test_kit_html_so_cria_pecas_html():
    texto = montar_relatorio(KitHtml(), itens_exemplo())
    assert all(linha.startswith("<") for linha in texto.splitlines())


def test_kit_texto_nao_tem_html():
    assert "<" not in montar_relatorio(KitTexto(), itens_exemplo())


def test_familia_nova_sem_mudar_o_cliente():
    linhas = montar_relatorio(KitMarkdown(), itens_exemplo()).splitlines()
    assert linhas[0] == "# Pharmas" and linhas[-1].startswith("**TOTAL")


def test_fabrica_abstrata_nao_cria_nada():
    with pytest.raises(NotImplementedError):
        KitRelatorio().criar_cabecalho("x")


def test_uma_linha_por_item_mais_cabecalho_e_rodape():
    itens = itens_exemplo()
    assert len(montar_relatorio(KitTexto(), itens).splitlines()) == len(itens) + 2
