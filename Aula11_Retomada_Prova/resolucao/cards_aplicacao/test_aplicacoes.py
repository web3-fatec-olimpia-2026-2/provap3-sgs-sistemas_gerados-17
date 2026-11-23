import json

import pytest

from aplicacoes import (ApiPagamentoTerceiro, CheckoutFacade, ComBercoExtra,
                        ComCafeDaManha, Conta, NotaFiscal, OpcaoQuartoViewModel,
                        PagamentoAdapter, Quartos, ReciboJsonFormatter,
                        ReciboTextoFormatter, Reserva, ReservaBase, ReservaService,
                        TarifaFidelidade, TarifaParceiro)


def test_card1_strategy_nova_tarifa_sem_tocar_na_reserva():
    assert Reserva(200, TarifaFidelidade()).total() == 180.0
    assert Reserva(200, TarifaParceiro()).total() == 160.0


def test_card2_formato_novo_por_extensao():
    assert ReciboTextoFormatter().formatar("Ana", 600) == "RECIBO\nAna\nTotal: R$ 600.00"
    assert json.loads(ReciboJsonFormatter().formatar("Ana", 600)) == {"hospede": "Ana", "total": 600}


@pytest.mark.parametrize("idade, categoria, pode", [
    (17, "suite", False), (18, "suite", True), (10, "comum", True),
])
def test_card3_regra_no_service(idade, categoria, pode):
    assert ReservaService().pode_reservar(idade, categoria) is pode


def test_card3_viewmodel_so_traduz():
    vm = OpcaoQuartoViewModel(15, "suite")
    assert vm.botao_label == "Indisponível para menores"
    assert vm.css == "btn-desabilitado"


def test_card4_adapter_traduz_reais_para_centavos_e_json():
    api = ApiPagamentoTerceiro()
    tx = PagamentoAdapter(api).processar(199.90)
    assert tx == "PG0001"
    assert api.recebidos[0] == {"amount_cents": 19990, "currency": "BRL"}


def test_card4_adapter_recusa():
    with pytest.raises(ValueError):
        PagamentoAdapter(ApiPagamentoTerceiro()).processar(0)


def test_card5_facade_orquestra_os_tres():
    quartos, nota = Quartos(), NotaFiscal()
    r = CheckoutFacade(Conta(), quartos, nota).finalizar(reserva_id=7, quarto=101)
    assert r == {"valor": 750.0, "nota": "NF-7"}
    assert quartos.liberados == [101]
    assert nota.emitidas == [(7, 750.0)]


def test_card6_decorator_novo_e_ordem_indiferente():
    a = ComBercoExtra(ComCafeDaManha(ReservaBase(200, 2)))
    b = ComCafeDaManha(ComBercoExtra(ReservaBase(200, 2)))
    assert a.preco() == b.preco() == 465.0      # 400 + 40 + 25
