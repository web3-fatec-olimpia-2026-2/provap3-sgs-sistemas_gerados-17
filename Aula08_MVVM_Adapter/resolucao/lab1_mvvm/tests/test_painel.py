"""Lab 1 MVVM — 8 testes ORIGINAIS (nenhum lê a tela) + os meus."""
from quartos import (QUARTOS, PainelQuartosVM, QuartoViewModel, tela_quartos,
                     tela_quartos_mvvm)

UM_LIVRE = {"numero": 101, "categoria": "comum", "diaria": 200.0, "ocupado": False}
UM_OCUPADO = {"numero": 201, "categoria": "suite", "diaria": 500.0, "ocupado": True}


# --- originais: QuartoViewModel ---
def test_quarto_livre_fica_disponivel():
    vm = QuartoViewModel(UM_LIVRE)
    assert vm.disponivel is True
    assert vm.status_label == "livre"
    assert vm.botao_label == "Reservar"


def test_quarto_ocupado_nao_fica_disponivel():
    vm = QuartoViewModel(UM_OCUPADO)
    assert vm.disponivel is False
    assert vm.status_label == "INDISPONIVEL"
    assert vm.botao_label == "(ocupado)"


def test_preco_vem_formatado():
    assert QuartoViewModel(UM_LIVRE).preco_formatado == "R$ 200.00"


def test_numero_e_categoria_preservados():
    vm = QuartoViewModel(UM_LIVRE)
    assert vm.numero == 101
    assert vm.categoria == "comum"


# --- originais: PainelQuartosVM ---
def test_painel_conta_quartos_livres():
    assert PainelQuartosVM([UM_LIVRE, UM_OCUPADO, UM_LIVRE]).livres == 2


def test_painel_com_vaga_mostra_rodape_de_contagem():
    assert PainelQuartosVM([UM_LIVRE, UM_OCUPADO]).rodape == "1 quarto(s) livre(s)"


def test_painel_sem_vaga_mostra_lotado():
    painel = PainelQuartosVM([UM_OCUPADO, UM_OCUPADO])
    assert painel.livres == 0
    assert painel.rodape == "LOTADO - nenhum quarto livre"


def test_painel_entrega_um_viewmodel_por_quarto():
    painel = PainelQuartosVM([UM_LIVRE, UM_OCUPADO])
    assert len(painel.itens) == 2
    assert all(isinstance(i, QuartoViewModel) for i in painel.itens)


# --- meus ---
def test_view_mvvm_produz_a_mesma_tela_que_a_original():
    # "Mudou ONDE a decisão mora, não O QUE aparece na tela."
    for cenario in (QUARTOS, [UM_OCUPADO], [UM_LIVRE, UM_LIVRE], []):
        assert tela_quartos_mvvm(cenario) == tela_quartos(cenario)


def test_painel_vazio_e_lotado():
    assert PainelQuartosVM([]).rodape == "LOTADO - nenhum quarto livre"


def test_preco_com_centavos():
    q = dict(UM_LIVRE, diaria=199.9)
    assert QuartoViewModel(q).preco_formatado == "R$ 199.90"
