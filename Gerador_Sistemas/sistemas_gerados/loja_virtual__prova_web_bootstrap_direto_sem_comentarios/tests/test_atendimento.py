import pytest

from nucleo.atendimento import AtendimentoFacade
from nucleo.atendimento_base import Calculadora, Disponibilidade, Notificador, Pagamentos, Registro
from tests.fabrica import criar

ORDEM = ["disponibilidade.esta_disponivel", "calculadora.calcular", "pagamentos.cobrar",
         "registro.registrar", "notificador.enviar"]


def montar(indisponiveis=(), recusar=False):
    log = []
    registro, notificador = Registro(log), Notificador(log)
    facade = AtendimentoFacade(Disponibilidade(indisponiveis, log), Calculadora(log),
                               Pagamentos(log, recusar), registro, notificador)
    return facade, log, registro, notificador


def test_caminho_feliz_na_ordem_certa():
    facade, log, registro, notificador = montar()
    item = criar()
    resultado = facade.concluir(501, item)
    assert resultado["ok"] is True and resultado["protocolo"] == 1 and resultado["total"] == item.total
    assert log == ORDEM
    assert registro.buscar(1)["recurso"] == 501
    assert len(notificador.enviadas) == 1


def test_indisponivel_aborta_antes_de_cobrar():
    facade, log, _, _ = montar(indisponiveis=[501])
    assert facade.concluir(501, criar()) == {"ok": False, "motivo": "indisponivel"}
    assert log == ORDEM[:1]


def test_pagamento_recusado_nao_registra_nem_notifica():
    facade, log, registro, notificador = montar(recusar=True)
    assert facade.concluir(501, criar()) == {"ok": False, "motivo": "pagamento recusado"}
    assert "registro.registrar" not in log and notificador.enviadas == []


def test_protocolos_sequenciais():
    facade, _, _, _ = montar()
    assert facade.concluir(501, criar())["protocolo"] == 1
    assert facade.concluir(502, criar(1))["protocolo"] == 2
