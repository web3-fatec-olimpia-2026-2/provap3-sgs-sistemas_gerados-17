import pytest

from nucleo.politicas import Cobranca, CobrancaComFuncao, PoliticaClube, PoliticaInteira, PoliticaMeia, PoliticaPromocional
from tests.fabrica import criar, itens_exemplo

PARES = [("inteira", PoliticaInteira), ("meia", PoliticaMeia), ("clube", PoliticaClube)]


def test_politica_nova_entra_sem_mudar_a_cobranca():
    item = criar()
    assert Cobranca(item, PoliticaPromocional()).valor() == round(item.total * 0.6, 2)


def test_qualquer_objeto_com_aplicar_serve():
    class PoliticaDeTeste:
        def aplicar(self, base):
            return 0

    assert Cobranca(criar(), PoliticaDeTeste()).valor() == 0


def test_politica_trocada_em_tempo_de_execucao():
    cobranca = Cobranca(criar(), PoliticaInteira())
    cobranca.politica = PoliticaClube()
    assert cobranca.valor() == round(cobranca.item.total * 0.8, 2)


def test_estrategia_como_funcao():
    item = criar()
    assert CobrancaComFuncao(item, lambda base: base).valor() == item.total
