"""Testes do MVVM: nenhum teste lê a tela — todos perguntam ao ViewModel."""
import pytest

from nucleo import antes_painel
from nucleo.painel import ITENS, ItemViewModel, PainelVM, tela_painel_mvvm

LIVRE = {"codigo": 301, "categoria": "c", "preco": 200.0, "disponivel": True}
OCUPADO = {"codigo": 302, "categoria": "c", "preco": 200.0, "disponivel": False}


def test_item_livre():
    vm = ItemViewModel(LIVRE)
    assert vm.disponivel is True
    assert (vm.status_label, vm.acao_label) == ('com assentos', 'Reservar')


def test_item_ocupado():
    vm = ItemViewModel(OCUPADO)
    assert vm.disponivel is False
    assert (vm.status_label, vm.acao_label) == ('ESGOTADO', '(lista de espera)')


def test_preco_formatado():
    assert ItemViewModel(dict(LIVRE, preco=99.9)).preco_formatado == "R$ 99.90"


def test_dados_preservados():
    vm = ItemViewModel(LIVRE)
    assert (vm.codigo, vm.categoria) == (301, "c")


def test_painel_conta_os_livres():
    assert PainelVM([LIVRE, OCUPADO, LIVRE]).livres == 2


def test_rodape_com_disponibilidade():
    assert PainelVM([LIVRE, OCUPADO]).rodape == "1 " + 'voo(s) com assento'


def test_rodape_sem_disponibilidade():
    assert PainelVM([OCUPADO, OCUPADO]).rodape == 'ESGOTADO - nenhum voo com assento'
    assert PainelVM([]).rodape == 'ESGOTADO - nenhum voo com assento'


def test_um_viewmodel_por_item():
    painel = PainelVM([LIVRE, OCUPADO])
    assert len(painel.itens) == 2 and all(isinstance(i, ItemViewModel) for i in painel.itens)


@pytest.mark.parametrize("cenario", [ITENS, [OCUPADO], [LIVRE, LIVRE], []])
def test_tela_mvvm_igual_a_original(cenario):
    assert tela_painel_mvvm(cenario) == antes_painel.tela_painel(cenario)
