"""
Testes da Facade. O cliente so fala com a RecepcaoFacade - nunca com os 4
subsistemas diretamente. Os testes conferem que a orquestracao acontece por dentro.
Rode:  python3 -m pytest -v
"""
from recepcao import (
    Disponibilidade, Tarifa, Reservas, Notificador, RecepcaoFacade,
)


def montar(ocupados=()):
    disp = Disponibilidade(ocupados)
    rep = Reservas()
    notif = Notificador()
    facade = RecepcaoFacade(disp, Tarifa(), rep, notif)
    return facade, rep, notif


def test_reserva_ok_devolve_id_e_total():
    facade, rep, notif = montar()
    r = facade.reservar(quarto=101, hospede="Ana", noites=3)
    assert r["ok"] is True
    assert r["reserva_id"] == 1
    assert r["total"] == 600.0          # 200 x 3


def test_reserva_ok_grava_no_repositorio():
    facade, rep, notif = montar()
    r = facade.reservar(quarto=201, hospede="Bruno", noites=2)
    gravada = rep.buscar(r["reserva_id"])
    assert gravada["hospede"] == "Bruno"
    assert gravada["total"] == 1000.0   # 500 x 2


def test_reserva_ok_notifica_o_hospede():
    facade, rep, notif = montar()
    facade.reservar(quarto=101, hospede="Ana", noites=1)
    assert notif.enviadas == [("Ana", "Reserva 1 confirmada - total R$ 200.00")]


def test_quarto_ocupado_nao_grava_nem_notifica():
    facade, rep, notif = montar(ocupados=[101])
    r = facade.reservar(quarto=101, hospede="Ana", noites=3)
    assert r == {"ok": False, "motivo": "indisponivel"}
    assert rep.buscar(1) is None        # nao gravou
    assert notif.enviadas == []         # nao notificou


def test_cliente_so_fala_com_a_facade():
    # a facade expoe UM ponto de entrada; o cliente nao precisa conhecer os 4
    facade, _, _ = montar()
    assert hasattr(facade, "reservar")
