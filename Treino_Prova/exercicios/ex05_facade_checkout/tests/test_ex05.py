import importlib
import os

import pytest

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))

ITENS = {"cafe": 2, "pao": 1}


def montar(saldo=None, recusar=False):
    log = []
    est = m.Estoque(saldo if saldo is not None else {"cafe": 5, "pao": 5}, log)
    pag = m.Pagamentos(log, recusar=recusar)
    nota, email = m.NotaFiscal(log), m.Email(log)
    return m.CheckoutFacade(est, pag, nota, email), log, est, nota, email


def test_caminho_feliz_na_ordem_certa():
    facade, log, est, nota, email = montar()
    r = facade.finalizar("ana", ITENS, 39.3)
    assert r == {"ok": True, "tx": "TX-ana-39.30", "nota": "NF001"}
    assert log == ["estoque.tem", "pagamentos.cobrar", "estoque.baixar", "nota.emitir", "email.enviar"]
    assert est.saldo("cafe") == 3
    assert email.enviados == [("ana", "Pedido confirmado - nota NF001")]


def test_sem_estoque_nao_cobra():
    facade, log, *_ = montar(saldo={"cafe": 1})
    assert facade.finalizar("ana", ITENS, 10) == {"ok": False, "motivo": "sem estoque"}
    assert log == ["estoque.tem"]


def test_pagamento_recusado_nao_baixa_estoque():
    facade, log, est, nota, email = montar(recusar=True)
    assert facade.finalizar("ana", ITENS, 10) == {"ok": False, "motivo": "pagamento recusado"}
    assert est.saldo("cafe") == 5 and nota.emitidas == [] and email.enviados == []
    assert "estoque.baixar" not in log


@pytest.mark.parametrize("saldo, recusar", [({"cafe": 5, "pao": 5}, False), ({"cafe": 0}, False),
                                            ({"cafe": 5, "pao": 5}, True)])
def test_equivale_a_orquestracao_na_mao(saldo, recusar):
    facade, log_f, *_ = montar(saldo, recusar)
    log_m = []
    na_mao = m.finalizar_na_mao("ana", ITENS, 10, m.Estoque(saldo, log_m), m.Pagamentos(log_m, recusar),
                                m.NotaFiscal(log_m), m.Email(log_m))
    assert facade.finalizar("ana", ITENS, 10) == na_mao
    assert log_f == log_m
