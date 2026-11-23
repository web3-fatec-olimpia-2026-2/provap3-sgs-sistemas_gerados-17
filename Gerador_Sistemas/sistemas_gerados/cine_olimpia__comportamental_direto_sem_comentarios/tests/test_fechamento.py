import pytest

from nucleo.fechamento import Fechamento, FechamentoMeia, FechamentoComTaxa, FechamentoPadrao
from tests.fabrica import itens_exemplo


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
    assert FechamentoMeia().fechar(item) == f"R$ {round(item.total * 0.5, 2):.2f}"


def test_subclasses_nao_sobrescrevem_o_template():
    for classe in (FechamentoPadrao, FechamentoComTaxa, FechamentoMeia):
        assert "fechar" not in vars(classe)
