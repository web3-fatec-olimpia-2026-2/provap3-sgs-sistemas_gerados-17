"""Testes do MVVM: nenhum teste lê a tela — todos perguntam ao ViewModel."""
import pytest

from nucleo.painel import ITENS, ItemViewModel, PainelVM, tela_painel_mvvm

LIVRE = {"codigo": 1, "categoria": "c", "preco": 200.0, "disponivel": True}
OCUPADO = {"codigo": 2, "categoria": "c", "preco": 200.0, "disponivel": False}


def test_item_livre():
    vm = ItemViewModel(LIVRE)
    assert vm.disponivel is True
    assert (vm.status_label, vm.acao_label) == ('disponível', 'Solicitar')


def test_item_ocupado():
    vm = ItemViewModel(OCUPADO)
    assert vm.disponivel is False
    assert (vm.status_label, vm.acao_label) == ('INDISPONÍVEL', '(indisponível)')


def test_preco_formatado():
    assert ItemViewModel(dict(LIVRE, preco=99.9)).preco_formatado == "R$ 99.90"


def test_dados_preservados():
    vm = ItemViewModel(LIVRE)
    assert (vm.codigo, vm.categoria) == (1, "c")


def test_painel_conta_os_livres():
    assert PainelVM([LIVRE, OCUPADO, LIVRE]).livres == 2


def test_rodape_com_disponibilidade():
    assert PainelVM([LIVRE, OCUPADO]).rodape == "1 " + 'recurso(s) disponível(is)'


def test_rodape_sem_disponibilidade():
    assert PainelVM([OCUPADO, OCUPADO]).rodape == 'SEM DISPONIBILIDADE'
    assert PainelVM([]).rodape == 'SEM DISPONIBILIDADE'


def test_um_viewmodel_por_item():
    painel = PainelVM([LIVRE, OCUPADO])
    assert len(painel.itens) == 2 and all(isinstance(i, ItemViewModel) for i in painel.itens)
