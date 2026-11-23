"""ex07 — confere o gabarito das Partes B (previsões) e D (extensões).
Parte D: por padrão testa extensoes_gabarito; ALVO=extensoes testa a sua."""
import importlib
import os

import pytest

from loja import (Carrinho, CheckoutFacade, ComCupom10, ComEmbrulho, EmailFake,
                  FretePAC, FreteRetirada, PedidoService, ResumoPedidoVM,
                  montar_checkout)

ext = importlib.import_module(os.environ.get("ALVO", "extensoes_gabarito"))


# ---------------- Parte B ----------------
def test_b1():
    r = montar_checkout().finalizar("ana", ComEmbrulho(Carrinho([("cafe", 30), ("caneca", 45)])),
                                    FretePAC(), 2, "tok_ok")
    assert r == {"ok": True, "tx": "PF-0001", "total": 104, "frete": 14}


def test_b2_cupom_por_fora():
    c = ComCupom10(ComEmbrulho(Carrinho([("cafeteira", 200)])))
    assert montar_checkout().finalizar("ana", c, FretePAC(), 3, "tok_ok")["total"] == 209.5


def test_b3_cupom_por_dentro():
    c = ComEmbrulho(ComCupom10(Carrinho([("cafeteira", 200)])))
    assert montar_checkout().finalizar("ana", c, FretePAC(), 3, "tok_ok")["total"] == 211.0


def test_b4_frete_gratis_ignora_o_peso():
    r = montar_checkout().finalizar("ana", Carrinho([("cafeteira", 200)]), FretePAC(), 30, "tok_ok")
    assert r["frete"] == 0 and r["total"] == 200


def test_b5_viewmodel():
    r = {"ok": True, "tx": "PF-0001", "total": 104, "frete": 14}
    vm = ResumoPedidoVM(r)
    assert (vm.valor_formatado, vm.frete_label) == ("R$ 104.00", "Frete R$ 14.00")


def test_b6_recusado_sem_email():
    email = EmailFake()
    from loja import GatewayPagaFacil, PagaFacilAdapter
    c = CheckoutFacade(PedidoService(), PagaFacilAdapter(GatewayPagaFacil()), email)
    assert c.finalizar("ana", Carrinho([("x", 10)]), FreteRetirada(), 1, "tok_recusado") == \
        {"ok": False, "motivo": "cartão recusado"}
    assert email.enviados == []


# ---------------- Parte D ----------------
def test_d1_motoboy_entra_sem_editar_o_service():
    total, frete = PedidoService().total(Carrinho([("x", 50)]), ext.FreteMotoboy(), 2)
    assert (total, frete) == (62, 12)
    with pytest.raises(ValueError):
        ext.FreteMotoboy().calcular(6)


def test_d2_seguro_empilha():
    p = ext.ComSeguro(ComEmbrulho(Carrinho([("x", 85)])))     # (85+15)*1.03
    assert p.preco() == 103.0
    assert p.descricao() == "Carrinho (1 itens) + embrulho + seguro"


def test_d3_pix_funciona_na_facade_sem_adapter():
    c = CheckoutFacade(PedidoService(), ext.ProcessadorPix(), EmailFake())
    assert c.finalizar("ana", Carrinho([("x", 300)]), FretePAC(), 1, "-")["tx"] == "PIX-0001"
