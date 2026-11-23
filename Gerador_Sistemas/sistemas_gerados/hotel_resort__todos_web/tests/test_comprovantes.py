"""Testes do BRIDGE: cada combinação = a classe antiga; formato novo serve a todos os tipos."""
import pytest

from nucleo import antes_comprovantes
from nucleo.comprovantes import (Comprovante, ComprovanteDetalhado, ComprovanteSimples, Formato, FormatoHtml,
                                 FormatoMarkdown, FormatoTexto)
from tests.fabrica import itens_exemplo

COMBINACOES = [(ComprovanteSimples, FormatoTexto, "SimplesTexto"), (ComprovanteSimples, FormatoHtml, "SimplesHtml"),
               (ComprovanteDetalhado, FormatoTexto, "DetalhadoTexto"),
               (ComprovanteDetalhado, FormatoHtml, "DetalhadoHtml")]


@pytest.mark.parametrize("tipo, formato, antiga", COMBINACOES)
@pytest.mark.parametrize("indice", range(4))
def test_cada_combinacao_igual_a_classe_antiga(tipo, formato, antiga, indice):
    item = itens_exemplo()[indice]
    assert tipo(formato()).gerar(item) == getattr(antes_comprovantes, antiga)().gerar(item)


@pytest.mark.parametrize("tipo", [ComprovanteSimples, ComprovanteDetalhado])
def test_formato_novo_vale_para_todos_os_tipos(tipo):
    texto = tipo(FormatoMarkdown()).gerar(itens_exemplo()[0])
    assert texto.startswith("## ") and "**Total**" in texto


def test_trocar_o_formato_em_tempo_de_execucao():
    comprovante = ComprovanteSimples(FormatoTexto())
    comprovante.formato = FormatoHtml()
    assert comprovante.gerar(itens_exemplo()[0]).startswith("<h2>")


def test_partes_abstratas():
    with pytest.raises(NotImplementedError):
        Comprovante(FormatoTexto()).gerar(itens_exemplo()[0])
    with pytest.raises(NotImplementedError):
        Formato().titulo("x")
