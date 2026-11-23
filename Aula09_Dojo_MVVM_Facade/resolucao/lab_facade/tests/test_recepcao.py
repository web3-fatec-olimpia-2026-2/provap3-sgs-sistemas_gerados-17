"""Lab Facade — 5 testes ORIGINAIS + os meus (equivalência com a versão 'na mão')."""
import pytest

from recepcao import (Disponibilidade, Notificador, RecepcaoFacade, Reservas,
                      Tarifa, criar_recepcao_padrao, fazer_reserva_na_mao)


def montar(ocupados=()):
    disp = Disponibilidade(ocupados)
    rep = Reservas()
    notif = Notificador()
    facade = RecepcaoFacade(disp, Tarifa(), rep, notif)
    return facade, rep, notif


# --- originais ---
def test_reserva_ok_devolve_id_e_total():
    facade, rep, notif = montar()
    r = facade.reservar(quarto=101, hospede="Ana", noites=3)
    assert r["ok"] is True
    assert r["reserva_id"] == 1
    assert r["total"] == 600.0


def test_reserva_ok_grava_no_repositorio():
    facade, rep, notif = montar()
    r = facade.reservar(quarto=201, hospede="Bruno", noites=2)
    gravada = rep.buscar(r["reserva_id"])
    assert gravada["hospede"] == "Bruno"
    assert gravada["total"] == 1000.0


def test_reserva_ok_notifica_o_hospede():
    facade, rep, notif = montar()
    facade.reservar(quarto=101, hospede="Ana", noites=1)
    assert notif.enviadas == [("Ana", "Reserva 1 confirmada - total R$ 200.00")]


def test_quarto_ocupado_nao_grava_nem_notifica():
    facade, rep, notif = montar(ocupados=[101])
    r = facade.reservar(quarto=101, hospede="Ana", noites=3)
    assert r == {"ok": False, "motivo": "indisponivel"}
    assert rep.buscar(1) is None
    assert notif.enviadas == []


def test_cliente_so_fala_com_a_facade():
    facade, _, _ = montar()
    assert hasattr(facade, "reservar")


# --- meus ---
@pytest.mark.parametrize("quarto, noites, ocupados", [
    (101, 3, ()), (201, 2, ()), (301, 1, ()), (101, 2, (101,)),
])
def test_facade_equivale_a_orquestracao_na_mao(quarto, noites, ocupados):
    facade, _, notif_f = montar(ocupados)
    disp, rep, notif_m = Disponibilidade(ocupados), Reservas(), Notificador()
    na_mao = fazer_reserva_na_mao(quarto, "X", noites, disp, Tarifa(), rep, notif_m)
    assert facade.reservar(quarto, "X", noites) == na_mao
    assert notif_f.enviadas == notif_m.enviadas


def test_ids_sequenciais_em_reservas_seguidas():
    facade, _, _ = montar()
    assert facade.reservar(101, "A", 1)["reserva_id"] == 1
    assert facade.reservar(201, "B", 1)["reserva_id"] == 2


def test_fabrica_de_recepcao_padrao():
    r = criar_recepcao_padrao(ocupados=[301]).reservar(301, "Ana", 1)
    assert r["ok"] is False
