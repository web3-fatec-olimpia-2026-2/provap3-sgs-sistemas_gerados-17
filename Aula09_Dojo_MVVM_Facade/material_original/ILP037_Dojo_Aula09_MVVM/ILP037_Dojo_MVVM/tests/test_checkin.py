"""
Testes do Dojo - CheckinViewModel. Nenhum le a tela: todos perguntam ao ViewModel.
Rode:  python3 -m pytest -v
"""
from checkin import CheckinViewModel

CONFIRMADA_PAGA = {"hospede": "Ana",   "quarto": 101, "status": "confirmada", "pago": True}
CONFIRMADA_NPAGA = {"hospede": "Bruno", "quarto": 201, "status": "confirmada", "pago": False}
PENDENTE = {"hospede": "Carla", "quarto": 301, "status": "pendente", "pago": False}


def test_confirmada_e_paga_pode_checkin():
    vm = CheckinViewModel(CONFIRMADA_PAGA)
    assert vm.pode_checkin is True
    assert vm.selo == "VERDE"
    assert vm.acao_label == "Fazer check-in"


def test_confirmada_sem_pagar_aguarda():
    vm = CheckinViewModel(CONFIRMADA_NPAGA)
    assert vm.pode_checkin is False
    assert vm.selo == "AMARELO"
    assert vm.acao_label == "Aguardando pagamento"


def test_pendente_nao_disponivel():
    vm = CheckinViewModel(PENDENTE)
    assert vm.pode_checkin is False
    assert vm.selo == "CINZA"
    assert vm.acao_label == "Nao disponivel"


def test_dados_preservados():
    vm = CheckinViewModel(CONFIRMADA_PAGA)
    assert vm.hospede == "Ana"
    assert vm.quarto == 101
