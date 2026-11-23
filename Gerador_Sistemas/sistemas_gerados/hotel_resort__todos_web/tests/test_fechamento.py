"""Testes do TEMPLATE METHOD: mesmo resultado das cópias; ordem fixa; subclasse muda um passo."""
import pytest

from nucleo.antes_fechamento import fechar_com_taxa_antigo, fechar_padrao_antigo
from nucleo.fechamento import Fechamento, FechamentoFidelidade, FechamentoComTaxa, FechamentoPadrao
from tests.fabrica import itens_exemplo


@pytest.mark.parametrize("indice", range(4))
def test_mesmo_resultado_das_copias_antigas(indice):
    item = itens_exemplo()[indice]
    assert FechamentoPadrao().fechar(item) == fechar_padrao_antigo(item)
    assert FechamentoComTaxa().fechar(item) == fechar_com_taxa_antigo(item)


def test_a_ordem_dos_passos_e_fixa():
    chamadas = []

    class Espiao(Fechamento):
        def validar(self, item):
            chamadas.append("validar")

        def calcular(self, item):
            chamadas.append("calcular")
            return 10.0

        def ajustar(self, valor):
            chamadas.append("ajustar")
            return valor

        def formatar(self, valor):
            chamadas.append("formatar")
            return str(valor)

    Espiao().fechar(itens_exemplo()[0])
    assert chamadas == ["validar", "calcular", "ajustar", "formatar"]


def test_gancho_padrao_nao_muda_o_valor():
    assert Fechamento().ajustar(123.45) == 123.45


def test_subclasse_nova_muda_so_um_passo():
    item = itens_exemplo()[0]
    assert FechamentoFidelidade().fechar(item) == f"R$ {round(item.total * 0.9, 2):.2f}"


def test_subclasses_nao_sobrescrevem_o_template():
    for classe in (FechamentoPadrao, FechamentoComTaxa, FechamentoFidelidade):
        assert "fechar" not in vars(classe)
