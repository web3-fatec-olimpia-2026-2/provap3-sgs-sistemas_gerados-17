import pytest

from nucleo.regras import E, Comparacao, Ou, ler_regra
from tests.fabrica import criar, itens_exemplo

REGRA = "quantidade >= 3 e total > 500 ou preco == 0"


def test_arvore_montada_a_mao_equivale_ao_texto():
    arvore = Ou(E(Comparacao("quantidade", ">=", 3), Comparacao("total", ">", 500)),
                E(Comparacao("preco", "==", 0)))
    for item in itens_exemplo():
        assert arvore.interpretar(item) == ler_regra(REGRA).interpretar(item)


def test_regra_nova_sem_mudar_codigo():
    item = criar(quantidade=2, preco=50.0)
    assert ler_regra("total <= 100").interpretar(item) is True
    assert ler_regra("quantidade > 2").interpretar(item) is False


@pytest.mark.parametrize("ruim", ["total >", "campo_inexistente > 3", "total ~ 3", "total > muito"])
def test_regra_mal_escrita_e_recusada(ruim):
    with pytest.raises(ValueError):
        ler_regra(ruim)
