import pytest

from nucleo.politicas import Cobranca, CobrancaComFuncao, PoliticaAtacado, PoliticaComum, PoliticaFidelidade, PoliticaFuncionario
from tests.fabrica import criar, itens_exemplo

PARES = [("comum", PoliticaComum), ("fidelidade", PoliticaFidelidade), ("atacado", PoliticaAtacado)]


def test_politica_nova_entra_sem_mudar_a_cobranca():
    item = criar()
    assert Cobranca(item, PoliticaFuncionario()).valor() == round(item.total * 0.7, 2)


def test_qualquer_objeto_com_aplicar_serve():
    class PoliticaDeTeste:
        def aplicar(self, base):
            return 0

    assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


def test_politica_trocada_em_tempo_de_execucao():
    cobranca = Cobranca(criar(), PoliticaComum())
    cobranca.politica = PoliticaAtacado()
    assert cobranca.valor() == round(cobranca.item.total * 0.85, 2)


def test_estrategia_como_funcao():
    item = criar()
    assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
