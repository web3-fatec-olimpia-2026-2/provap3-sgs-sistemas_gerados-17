"""Testes do STRATEGY: o resultado não muda (antes × depois) e a extensão não toca no contexto."""
import pytest

from nucleo.politicas import Cobranca, CobrancaComFuncao, PoliticaComum, PoliticaEstudante, PoliticaProfessor, PoliticaVisitante
from tests.fabrica import criar, itens_exemplo

PARES = [("comum", PoliticaComum), ("estudante", PoliticaEstudante), ("professor", PoliticaProfessor)]


def test_politica_nova_entra_sem_mudar_a_cobranca():
    item = criar()
    assert Cobranca(item, PoliticaVisitante()).valor() == round(item.total * 1.5, 2)


def test_qualquer_objeto_com_aplicar_serve():
    class PoliticaDeTeste:
        def aplicar(self, base):
            return 0

    assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


def test_politica_trocada_em_tempo_de_execucao():
    cobranca = Cobranca(criar(), PoliticaComum())
    cobranca.politica = PoliticaProfessor()
    assert cobranca.valor() == round(cobranca.item.total * 0.7, 2)


def test_estrategia_como_funcao():
    item = criar()
    assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
