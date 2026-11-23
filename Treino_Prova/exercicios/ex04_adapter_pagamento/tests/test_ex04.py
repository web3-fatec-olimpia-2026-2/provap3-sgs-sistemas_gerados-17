import importlib
import os

import pytest

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))


def test_adapter_e_um_processador():
    assert isinstance(m.PagaFacilAdapter(m.GatewayPagaFacil()), m.ProcessadorPagamento)


def test_traduz_reais_para_centavos_inteiros():
    gw = m.GatewayPagaFacil()
    m.PagaFacilAdapter(gw).processar(19.99, "tok_123")
    assert gw.recebidos[0] == {"amount_cents": 1999, "card": "tok_123", "currency": "BRL"}
    assert isinstance(gw.recebidos[0]["amount_cents"], int)


def test_aprovado_devolve_id():
    assert m.PagaFacilAdapter(m.GatewayPagaFacil()).processar(10, "tok_1") == "PF-0001"


def test_recusado_vira_excecao_de_dominio():
    with pytest.raises(m.PagamentoRecusado, match="recusado"):
        m.PagaFacilAdapter(m.GatewayPagaFacil()).processar(10, "tok_recusado")


@pytest.fixture(params=["fake", "pagafacil"])
def processador(request):
    return m.ProcessadorFake() if request.param == "fake" else m.PagaFacilAdapter(m.GatewayPagaFacil())


def test_checkout_funciona_com_qualquer_processador(processador):
    checkout = m.Checkout(processador)
    assert checkout.pagar(50, "tok_ok")["ok"] is True
    assert checkout.pagar(50, "tok_recusado") == {"ok": False, "motivo": "cartão recusado"}


@pytest.mark.parametrize("token", ["tok_ok", "tok_recusado"])
def test_mesmo_resultado_que_o_checkout_antigo(token):
    novo = m.Checkout(m.PagaFacilAdapter(m.GatewayPagaFacil())).pagar(30, token)
    antigo = m.CheckoutAntigo(None, m.GatewayPagaFacil(), usa_pagafacil=True).pagar(30, token)
    assert novo == antigo
