from nucleo.orcamento import (CalculoDoTotal, ContagemPorTipo, LinhaIngresso, LinhaDesconto, LinhaExtra, Orcamento,
                              TextoDoOrcamento)
from tests.fabrica import itens_exemplo

EXTRAS = [("pipoca", 25.0), ("refrigerante", 12.0)]


def montar():
    a, b, _, _ = itens_exemplo()
    linhas = [LinhaIngresso(a), LinhaIngresso(b), LinhaExtra(*EXTRAS[0]), LinhaExtra(*EXTRAS[1]), LinhaDesconto(5.0)]
    tuplas = [("ingresso", a), ("ingresso", b), ("extra", *EXTRAS[0]), ("extra", *EXTRAS[1]), ("desconto", 5.0)]
    return Orcamento(linhas), tuplas


def test_operacao_nova_sem_mudar_as_linhas():
    orcamento, _ = montar()
    assert orcamento.aceitar(ContagemPorTipo()) == {"ingresso": 2, "extra": 2, "desconto": 1}


def test_despacho_duplo_chama_o_metodo_do_tipo():
    chamadas = []

    class Espiao:
        def visitar_ingresso(self, linha):
            chamadas.append("ingresso")

        def visitar_extra(self, linha):
            chamadas.append("extra")

        def visitar_desconto(self, linha):
            chamadas.append("desconto")

        def resultado(self):
            return chamadas

    orcamento, _ = montar()
    assert orcamento.aceitar(Espiao()) == ["ingresso", "ingresso", "extra", "extra", "desconto"]


def test_orcamento_vazio():
    assert Orcamento([]).aceitar(CalculoDoTotal()) == 0
