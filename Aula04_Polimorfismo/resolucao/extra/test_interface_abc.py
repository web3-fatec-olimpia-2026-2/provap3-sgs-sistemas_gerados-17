import pytest

from interface_abc import Boleto, Cartao, FormaPagamento, Pix, cobrar


def test_cada_forma_responde_a_seu_modo():
    assert cobrar(Pix(), 100) == 95.0
    assert cobrar(Cartao(), 100) == 103.0
    assert cobrar(Boleto(), 100) == 102.5


def test_nao_da_para_instanciar_a_interface():
    with pytest.raises(TypeError):
        FormaPagamento()


def test_subtipo_que_esquece_o_metodo_nao_nasce():
    class Esquecida(FormaPagamento):
        pass

    with pytest.raises(TypeError):
        Esquecida()
