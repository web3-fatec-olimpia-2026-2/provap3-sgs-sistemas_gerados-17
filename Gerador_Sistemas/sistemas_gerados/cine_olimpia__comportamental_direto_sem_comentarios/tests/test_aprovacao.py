import pytest

from nucleo.aprovacao import Atendente, Diretoria, Gerente, Supervisor, cadeia_padrao
from tests.fabrica import criar

VALORES = [0.0, 100.0, 500.0, 500.01, 1500.0, 2000.0, 9999.99, 10000.0, 10000.01, 50000.0]


def item_de(valor):
    return criar(quantidade=1, preco=valor)


@pytest.mark.parametrize("valor, esperado", [(100.0, "atendente"), (1500.0, "gerente"),
                                             (5000.0, "diretoria"), (50000.0, "sem aprovador")])
def test_cada_elo_aprova_a_sua_alcada(valor, esperado):
    assert cadeia_padrao().aprovar(item_de(valor)) == esperado


def test_nivel_novo_entra_sem_mudar_os_outros():
    inicio = Atendente()
    inicio.encadear(Supervisor()).encadear(Gerente()).encadear(Diretoria())
    assert inicio.aprovar(item_de(800.0)) == "supervisor"
    assert inicio.aprovar(item_de(1500.0)) == "gerente"


def test_elo_sozinho_sem_alcada_nao_aprova():
    assert Atendente().aprovar(item_de(600.0)) == "sem aprovador"


def test_encadear_devolve_o_proximo():
    gerente = Gerente()
    assert Atendente().encadear(gerente) is gerente
