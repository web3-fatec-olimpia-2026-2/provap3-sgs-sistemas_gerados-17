"""
Testes do painel de quartos.

Repare: NENHUM teste procura texto dentro da tela. Eles batem direto na
camada ViewModel, que prepara os dados. Testar a REGRA ficou separado de
testar o DESENHO. Isso e o que o MVVM nos da.

Rode:   python3 -m pytest -v
"""
from quartos import QuartoViewModel, PainelQuartosVM

UM_LIVRE = {"numero": 101, "categoria": "comum", "diaria": 200.0, "ocupado": False}
UM_OCUPADO = {"numero": 201, "categoria": "suite", "diaria": 500.0, "ocupado": True}


# --- QuartoViewModel: prepara UM quarto ------------------------------------
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
    vm = QuartoViewModel(UM_LIVRE)
    assert vm.preco_formatado == "R$ 200.00"


def test_numero_e_categoria_preservados():
    vm = QuartoViewModel(UM_LIVRE)
    assert vm.numero == 101
    assert vm.categoria == "comum"


# --- PainelQuartosVM: prepara o PAINEL --------------------------------------
def test_painel_conta_quartos_livres():
    painel = PainelQuartosVM([UM_LIVRE, UM_OCUPADO, UM_LIVRE])
    assert painel.livres == 2


def test_painel_com_vaga_mostra_rodape_de_contagem():
    painel = PainelQuartosVM([UM_LIVRE, UM_OCUPADO])
    assert painel.rodape == "1 quarto(s) livre(s)"


def test_painel_sem_vaga_mostra_lotado():
    painel = PainelQuartosVM([UM_OCUPADO, UM_OCUPADO])
    assert painel.livres == 0
    assert painel.rodape == "LOTADO - nenhum quarto livre"


def test_painel_entrega_um_viewmodel_por_quarto():
    painel = PainelQuartosVM([UM_LIVRE, UM_OCUPADO])
    assert len(painel.itens) == 2
    assert all(isinstance(i, QuartoViewModel) for i in painel.itens)
