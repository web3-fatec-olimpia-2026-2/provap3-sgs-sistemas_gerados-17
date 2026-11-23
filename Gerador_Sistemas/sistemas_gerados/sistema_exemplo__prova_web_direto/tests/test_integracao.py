"""Testes do ADAPTER: tradução de chamada, dados e resposta + substituibilidade."""
import pytest

from nucleo.integracao import PagaJaAdapter, CheckoutService
from nucleo.integracao_base import GatewayPagaJa, PagamentoRecusado, ProcessadorInterno, ProcessadorPagamento
from tests.fabrica import criar


def test_adapter_e_um_processador():
    assert isinstance(PagaJaAdapter(GatewayPagaJa()), ProcessadorPagamento)


def test_traduz_reais_para_centavos_inteiros():
    gateway = GatewayPagaJa()
    PagaJaAdapter(gateway).processar(19.99, "tok_ok")
    assert gateway.recebidos[0] == {"amount_cents": 1999, "card": "tok_ok", "currency": "BRL"}
    assert isinstance(gateway.recebidos[0]["amount_cents"], int)


def test_aprovado_devolve_o_id():
    assert PagaJaAdapter(GatewayPagaJa()).processar(10, "tok_ok") == "PJ-0001"


def test_recusado_vira_excecao_do_sistema():
    with pytest.raises(PagamentoRecusado, match="recusado"):
        PagaJaAdapter(GatewayPagaJa()).processar(10, "tok_recusado")


@pytest.fixture(params=["interno", "gateway"])
def processador(request):
    return ProcessadorInterno() if request.param == "interno" else PagaJaAdapter(GatewayPagaJa())


def test_checkout_funciona_com_qualquer_processador(processador):
    item = criar()
    resultado = CheckoutService(processador).pagar(item, "tok_ok")
    assert resultado["ok"] is True and resultado["valor"] == item.total
    assert CheckoutService(processador).pagar(item, "tok_recusado") == {"ok": False, "motivo": "cartão recusado"}
