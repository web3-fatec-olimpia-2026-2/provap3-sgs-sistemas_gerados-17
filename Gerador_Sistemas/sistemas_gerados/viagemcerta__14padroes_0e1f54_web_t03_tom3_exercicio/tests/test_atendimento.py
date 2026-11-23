"""Testes do FACADE: ordem dos passos, regras de aborto e equivalência com a versão 'na mão'."""
import pytest

from nucleo.antes_atendimento import atender_na_mao
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
    resultado = facade.concluir(301, item)
    assert resultado["ok"] is True and resultado["protocolo"] == 1 and resultado["total"] == item.total
    assert log == ORDEM
    assert registro.buscar(1)["recurso"] == 301
    assert len(notificador.enviadas) == 1


def test_indisponivel_aborta_antes_de_cobrar():
    facade, log, _, _ = montar(indisponiveis=[301])
    assert facade.concluir(301, criar()) == {"ok": False, "motivo": "indisponivel"}
    assert log == ORDEM[:1]


def test_pagamento_recusado_nao_registra_nem_notifica():
    facade, log, registro, notificador = montar(recusar=True)
    assert facade.concluir(301, criar()) == {"ok": False, "motivo": "pagamento recusado"}
    assert "registro.registrar" not in log and notificador.enviadas == []


@pytest.mark.parametrize("indisponiveis, recusar", [((), False), ((301,), False), ((), True)])
def test_equivale_a_orquestracao_na_mao(indisponiveis, recusar):
    facade, log_fachada, _, _ = montar(indisponiveis, recusar)
    log_mao = []
    na_mao = atender_na_mao(301, criar(), Disponibilidade(indisponiveis, log_mao), Calculadora(log_mao),
                            Pagamentos(log_mao, recusar), Registro(log_mao), Notificador(log_mao))
    assert facade.concluir(301, criar()) == na_mao
    assert log_fachada == log_mao


def test_protocolos_sequenciais():
    facade, _, _, _ = montar()
    assert facade.concluir(301, criar())["protocolo"] == 1
    assert facade.concluir(302, criar(1))["protocolo"] == 2
