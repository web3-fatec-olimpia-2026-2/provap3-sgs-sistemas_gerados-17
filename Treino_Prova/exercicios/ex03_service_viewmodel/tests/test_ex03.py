import importlib
import os
from datetime import date

import pytest

m = importlib.import_module(os.environ.get("ALVO", "gabarito"))
HOJE = date(2026, 11, 21)


def pedido(**kw):
    base = {"id": 9, "cliente": "X", "valor_itens": 100.0, "cupom": False,
            "prazo": date(2026, 11, 25), "entregue": False}
    base.update(kw)
    return base


# --- Service: regra testada SEM tela ---
@pytest.mark.parametrize("valor, cupom, esperado", [
    (100.0, True, 90.0), (99.99, True, 99.99), (250.0, False, 250.0),
])
def test_service_total(valor, cupom, esperado):
    assert m.PedidoService().total(pedido(valor_itens=valor, cupom=cupom)) == pytest.approx(esperado)


def test_service_atraso():
    s = m.PedidoService()
    assert s.esta_atrasado(pedido(prazo=date(2026, 11, 20)), HOJE) is True
    assert s.esta_atrasado(pedido(prazo=date(2026, 11, 21)), HOJE) is False   # no dia não atrasou
    assert s.esta_atrasado(pedido(prazo=date(2026, 11, 1), entregue=True), HOJE) is False


# --- ViewModel: exibição testada sem renderizar ---
def test_vm_atrasado_fica_vermelho():
    vm = m.PedidoViewModel(pedido(prazo=date(2026, 11, 1)), HOJE)
    assert (vm.status_label, vm.cor) == ("ATRASADO", "vermelho")


def test_vm_formata_total_com_cupom():
    assert m.PedidoViewModel(pedido(cupom=True), HOJE).total_formatado == "R$ 90.00"


def test_vm_pergunta_ao_service():
    class ServiceFake:
        def total(self, p): return 1.0
        def esta_atrasado(self, p, hoje): return True

    vm = m.PedidoViewModel(pedido(), HOJE, servico=ServiceFake())
    assert vm.total_formatado == "R$ 1.00" and vm.status_label == "ATRASADO"


def test_painel_rodape():
    assert m.PainelPedidosVM(m.PEDIDOS, HOJE).rodape == "1 pedido(s) atrasado(s)"
    assert m.PainelPedidosVM([], HOJE).rodape == "Tudo em dia"


def test_tela_identica():
    assert m.tela_pedidos_mvvm(m.PEDIDOS, HOJE) == m.tela_pedidos(m.PEDIDOS, HOJE)
