"""Testes do VISITOR: mesmas operações da versão com if; operação nova sem mexer nas linhas."""
from nucleo.antes_orcamento import texto_antigo, total_antigo
from nucleo.orcamento import (CalculoDoTotal, ContagemPorTipo, LinhaPharm, LinhaDesconto, LinhaExtra, Orcamento,
                              TextoDoOrcamento)
from tests.fabrica import itens_exemplo

EXTRAS = [("urgente", 30.0), ("embalagem", 10.0)]  # (descrição, valor)


def montar():
    a, b, _, _ = itens_exemplo()
    linhas = [LinhaPharm(a), LinhaPharm(b), LinhaExtra(*EXTRAS[0]), LinhaExtra(*EXTRAS[1]), LinhaDesconto(5.0)]
    tuplas = [("pharm", a), ("pharm", b), ("extra", *EXTRAS[0]), ("extra", *EXTRAS[1]), ("desconto", 5.0)]
    return Orcamento(linhas), tuplas


def test_total_igual_a_versao_com_if():
    orcamento, tuplas = montar()
    assert orcamento.aceitar(CalculoDoTotal()) == total_antigo(tuplas)


def test_texto_igual_a_versao_com_if():
    orcamento, tuplas = montar()
    assert orcamento.aceitar(TextoDoOrcamento()) == texto_antigo(tuplas)


def test_operacao_nova_sem_mudar_as_linhas():
    orcamento, _ = montar()
    assert orcamento.aceitar(ContagemPorTipo()) == {"pharm": 2, "extra": 2, "desconto": 1}


def test_despacho_duplo_chama_o_metodo_do_tipo():
    chamadas = []

    class Espiao:
        def visitar_pharm(self, linha):
            chamadas.append("pharm")

        def visitar_extra(self, linha):
            chamadas.append("extra")

        def visitar_desconto(self, linha):
            chamadas.append("desconto")

        def resultado(self):
            return chamadas

    orcamento, _ = montar()
    assert orcamento.aceitar(Espiao()) == ["pharm", "pharm", "extra", "extra", "desconto"]


def test_orcamento_vazio():
    assert Orcamento([]).aceitar(CalculoDoTotal()) == 0
