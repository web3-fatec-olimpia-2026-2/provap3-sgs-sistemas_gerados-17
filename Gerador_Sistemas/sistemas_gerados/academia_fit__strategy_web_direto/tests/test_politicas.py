"""Testes do STRATEGY: o resultado não muda (antes × depois) e a extensão não toca no contexto."""
import pytest

from nucleo.politicas import Cobranca, CobrancaComFuncao, PoliticaCorporativo, PoliticaFamilia, PoliticaMensal, PoliticaUniversitario
from tests.fabrica import criar, itens_exemplo

PARES = [("mensal", PoliticaMensal), ("universitario", PoliticaUniversitario), ("corporativo", PoliticaCorporativo)]


def test_politica_nova_entra_sem_mudar_a_cobranca():
    item = criar()
    assert Cobranca(item, PoliticaFamilia()).valor() == round(item.total * 0.6, 2)


def test_qualquer_objeto_com_aplicar_serve():
    class PoliticaDeTeste:
        def aplicar(self, base):
            return 0

    assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


def test_politica_trocada_em_tempo_de_execucao():
    cobranca = Cobranca(criar(), PoliticaMensal())
    cobranca.politica = PoliticaCorporativo()
    assert cobranca.valor() == round(cobranca.item.total * 0.8, 2)


def test_estrategia_como_funcao():
    item = criar()
    assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
