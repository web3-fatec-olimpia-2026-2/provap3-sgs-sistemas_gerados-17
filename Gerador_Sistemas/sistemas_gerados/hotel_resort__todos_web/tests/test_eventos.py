"""Testes do OBSERVER: todos os inscritos são avisados; cancelar funciona; inválido não avisa."""
import pytest

from nucleo.antes_eventos import alterar_antigo
from nucleo.eventos import AlertaObservador, LogObservador, PainelObservador, ReservaObservavel
from tests.fabrica import criar


def test_todos_os_inscritos_sao_avisados():
    sujeito = ReservaObservavel(criar())
    painel, log = PainelObservador(), LogObservador()
    sujeito.inscrever(painel)
    sujeito.inscrever(log)
    sujeito.alterar("diarias", 3)
    assert painel.total == sujeito.item.total and len(log.linhas) == 1


def test_cancelado_nao_recebe_mais():
    sujeito = ReservaObservavel(criar())
    log = LogObservador()
    sujeito.inscrever(log)
    sujeito.alterar("diarias", 3)
    sujeito.cancelar(log)
    sujeito.alterar("diarias", 4)
    assert len(log.linhas) == 1


def test_alteracao_invalida_nao_avisa_ninguem():
    sujeito = ReservaObservavel(criar())
    log = LogObservador()
    sujeito.inscrever(log)
    with pytest.raises(ValueError):
        sujeito.alterar("diarias", 0)
    assert log.linhas == []


def test_observador_novo_sem_mudar_o_sujeito():
    sujeito = ReservaObservavel(criar(diarias=1))
    limite = sujeito.item.total + 0.01
    alerta = AlertaObservador(limite)
    sujeito.inscrever(alerta)
    sujeito.alterar("diarias", 2)
    assert alerta.alertas == [f"total passou de R$ {limite:.2f}"]


def test_mesmo_efeito_da_versao_antiga():
    a, b = criar(), criar()
    painel_antigo, log_antigo = {}, []
    alterar_antigo(a, "diarias", 3, painel_antigo, log_antigo)
    sujeito = ReservaObservavel(b)
    painel, log = PainelObservador(), LogObservador()
    sujeito.inscrever(painel)
    sujeito.inscrever(log)
    sujeito.alterar("diarias", 3)
    assert (painel.total, log.linhas) == (painel_antigo["total"], log_antigo)
