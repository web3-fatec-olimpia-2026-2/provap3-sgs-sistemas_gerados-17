import pytest

from nucleo.integracao import PagueMaisAdapter, CheckoutService
from nucleo.integracao_base import GatewayPagueMais, PagamentoRecusado, ProcessadorInterno, ProcessadorPagamento
from tests.fabrica import criar


def test_adapter_e_um_processador():
    assert isinstance(PagueMaisAdapter(GatewayPagueMais()), ProcessadorPagamento)


def test_traduz_reais_para_centavos_inteiros():
    gateway = GatewayPagueMais()
    PagueMaisAdapter(gateway).processar(19.99, "tok_ok")
    assert gateway.recebidos[0] == {"amount_cents": 1999, "card": "tok_ok", "currency": "BRL"}
    assert isinstance(gateway.recebidos[0]["amount_cents"], int)


def test_aprovado_devolve_o_id():
    assert PagueMaisAdapter(GatewayPagueMais()).processar(10, "tok_ok") == "PM-0001"


def test_recusado_vira_excecao_do_sistema():
    with pytest.raises(PagamentoRecusado, match="recusado"):
        PagueMaisAdapter(GatewayPagueMais()).processar(10, "tok_recusado")


@pytest.fixture(params=["interno", "gateway"])
def processador(request):
    return ProcessadorInterno() if request.param == "interno" else PagueMaisAdapter(GatewayPagueMais())


def test_checkout_funciona_com_qualquer_processador(processador):
    item = criar()
    resultado = CheckoutService(processador).pagar(item, "tok_ok")
    assert resultado["ok"] is True and resultado["valor"] == item.total
    assert CheckoutService(processador).pagar(item, "tok_recusado") == {"ok": False, "motivo": "cartão recusado"}
