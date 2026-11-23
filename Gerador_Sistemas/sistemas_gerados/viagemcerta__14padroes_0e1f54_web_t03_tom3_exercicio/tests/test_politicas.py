"""Testes do STRATEGY: o resultado não muda (antes × depois) e a extensão não toca no contexto."""
import pytest

from nucleo.antes_politicas import CobrancaAntiga
from nucleo.politicas import Cobranca, CobrancaComFuncao, PoliticaComum, PoliticaCorporativo, PoliticaEstudante, PoliticaFidelidade
from tests.fabrica import criar, itens_exemplo

PARES = [("comum", PoliticaComum), ("fidelidade", PoliticaFidelidade), ("corporativo", PoliticaCorporativo)]


@pytest.mark.parametrize("tipo, classe", PARES)
@pytest.mark.parametrize("indice", range(4))
def test_refatoracao_preserva_o_resultado(tipo, classe, indice):
    item = itens_exemplo()[indice]
    assert Cobranca(item, classe()).valor() == CobrancaAntiga(item, tipo).valor()


def test_politica_nova_entra_sem_mudar_a_cobranca():
    item = criar()
    assert Cobranca(item, PoliticaEstudante()).valor() == round(item.total * 0.8, 2)


def test_versao_com_if_nao_conhece_a_politica_nova():
    with pytest.raises(ValueError):
        CobrancaAntiga(criar(), "estudante").valor()


def test_qualquer_objeto_com_aplicar_serve():
    class PoliticaDeTeste:
        def aplicar(self, base):
            return 0

    assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


def test_politica_trocada_em_tempo_de_execucao():
    cobranca = Cobranca(criar(), PoliticaComum())
    cobranca.politica = PoliticaCorporativo()
    assert cobranca.valor() == round(cobranca.item.total * 0.85, 2)


def test_estrategia_como_funcao():
    item = criar()
    assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
