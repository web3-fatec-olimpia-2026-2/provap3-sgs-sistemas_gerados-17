from hw04a_sobrescreva import Bangalo, Presidencial, Quarto, imprimir_diaria


def test_subtipos_sao_quartos():
    assert isinstance(Presidencial(1), Quarto)
    assert isinstance(Bangalo(2), Quarto)


def test_laco_polimorfico():
    saidas = [imprimir_diaria(q) for q in (Quarto(1), Presidencial(2), Bangalo(3))]
    assert saidas == [
        "Quarto comum: R$ 200",
        "Quarto presidencial: R$ 1200",
        "Bangalo: R$ 440",
    ]
