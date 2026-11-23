import pytest

from nucleo.painel import ITENS, ItemViewModel, PainelVM, tela_painel_mvvm

LIVRE = {"codigo": 501, "categoria": "c", "preco": 200.0, "disponivel": True}
OCUPADO = {"codigo": 502, "categoria": "c", "preco": 200.0, "disponivel": False}


def test_item_livre():
    vm = ItemViewModel(LIVRE)
    assert vm.disponivel is True
    assert (vm.status_label, vm.acao_label) == ('em estoque', 'Comprar')


def test_item_ocupado():
    vm = ItemViewModel(OCUPADO)
    assert vm.disponivel is False
    assert (vm.status_label, vm.acao_label) == ('ESGOTADO', '(avise-me)')


def test_preco_formatado():
    assert ItemViewModel(dict(LIVRE, preco=99.9)).preco_formatado == "R$ 99.90"


def test_dados_preservados():
    vm = ItemViewModel(LIVRE)
    assert (vm.codigo, vm.categoria) == (501, "c")


def test_painel_conta_os_livres():
    assert PainelVM([LIVRE, OCUPADO, LIVRE]).livres == 2


def test_rodape_com_disponibilidade():
    assert PainelVM([LIVRE, OCUPADO]).rodape == "1 " + 'produto(s) em estoque'


def test_rodape_sem_disponibilidade():
    assert PainelVM([OCUPADO, OCUPADO]).rodape == 'SEM ESTOQUE - nenhum produto disponível'
    assert PainelVM([]).rodape == 'SEM ESTOQUE - nenhum produto disponível'


def test_um_viewmodel_por_item():
    painel = PainelVM([LIVRE, OCUPADO])
    assert len(painel.itens) == 2 and all(isinstance(i, ItemViewModel) for i in painel.itens)
