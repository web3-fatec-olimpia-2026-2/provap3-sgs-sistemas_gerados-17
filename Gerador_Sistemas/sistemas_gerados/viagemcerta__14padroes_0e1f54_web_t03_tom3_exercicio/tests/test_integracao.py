"""Testes do ADAPTER: tradução de chamada, dados e resposta + substituibilidade."""
import pytest

from nucleo.antes_integracao import CheckoutAntigo
from nucleo.integracao import PagaTurAdapter, CheckoutService
from nucleo.integracao_base import GatewayPagaTur, PagamentoRecusado, ProcessadorInterno, ProcessadorPagamento
from tests.fabrica import criar


def test_adapter_e_um_processador():
    assert isinstance(PagaTurAdapter(GatewayPagaTur()), ProcessadorPagamento)


def test_traduz_reais_para_centavos_inteiros():
    gateway = GatewayPagaTur()
    PagaTurAdapter(gateway).processar(19.99, "tok_ok")
    assert gateway.recebidos[0] == {"amount_cents": 1999, "card": "tok_ok", "currency": "BRL"}
    assert isinstance(gateway.recebidos[0]["amount_cents"], int)


def test_aprovado_devolve_o_id():
    assert PagaTurAdapter(GatewayPagaTur()).processar(10, "tok_ok") == "PT-0001"


def test_recusado_vira_excecao_do_sistema():
    with pytest.raises(PagamentoRecusado, match="recusado"):
        PagaTurAdapter(GatewayPagaTur()).processar(10, "tok_recusado")


@pytest.fixture(params=["interno", "gateway"])
def processador(request):
    return ProcessadorInterno() if request.param == "interno" else PagaTurAdapter(GatewayPagaTur())


def test_checkout_funciona_com_qualquer_processador(processador):
    item = criar()
    resultado = CheckoutService(processador).pagar(item, "tok_ok")
    assert resultado["ok"] is True and resultado["valor"] == item.total
    assert CheckoutService(processador).pagar(item, "tok_recusado") == {"ok": False, "motivo": "cartão recusado"}


@pytest.mark.parametrize("token", ["tok_ok", "tok_recusado"])
def test_mesmo_resultado_que_o_checkout_com_if(token):
    item = criar()
    novo = CheckoutService(PagaTurAdapter(GatewayPagaTur())).pagar(item, token)
    antigo = CheckoutAntigo(ProcessadorInterno(), GatewayPagaTur(), usa_gateway=True).pagar(item, token)
    assert novo == antigo
