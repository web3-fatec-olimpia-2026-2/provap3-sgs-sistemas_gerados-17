"""Confere o gabarito de 02_prever_o_resultado.md rodando o código REAL dos laboratórios
resolvidos (Aulas 05, 08, 09 e 10). Só rode depois de ter previsto no papel.

Como vários labs têm módulos com o mesmo nome (reserva.py, quartos.py...), carrego cada
arquivo pelo caminho, com um nome único, em vez de mexer no sys.path.
"""
import importlib.util
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]      # pasta do projeto


def carregar(nome_unico, caminho_relativo):
    caminho = RAIZ / caminho_relativo
    spec = importlib.util.spec_from_file_location(nome_unico, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


decorator = carregar("lab10_reserva", "Aula10_Sprint3_Decorator/resolucao/lab/reserva.py")
strategy = carregar("lab05_tarifa", "Aula05_Strategy/resolucao/lab/tarifa.py")
adapter = carregar("lab08_reservas", "Aula08_MVVM_Adapter/resolucao/lab2_adapter/reservas.py")
mvvm = carregar("lab08_quartos", "Aula08_MVVM_Adapter/resolucao/lab1_mvvm/quartos.py")
facade = carregar("lab09_recepcao", "Aula09_Dojo_MVVM_Facade/resolucao/lab_facade/recepcao.py")


def test_p1_decorator_preco_e_ordem_da_descricao():
    r = decorator.ComCafeDaManha(decorator.ComLateCheckout(decorator.ReservaBase(150, 3)))
    assert r.preco() == 550.0
    assert r.descricao() == "Reserva 3 noite(s) + late checkout + cafe da manha"


def test_p2_strategy_trocada():
    r = strategy.Reserva(2, 300, strategy.TarifaComum())
    assert r.total() == 600
    r.tarifa = strategy.TarifaParceiro()
    assert r.total() == 480.0


def test_p3_property_preserva_estado_valido(capsys):
    class Conta:
        def __init__(self, saldo):
            self.saldo = saldo

        @property
        def saldo(self):
            return self._saldo

        @saldo.setter
        def saldo(self, v):
            if v < 0:
                raise ValueError("negativo")
            self._saldo = v

    c = Conta(100)
    with pytest.raises(ValueError, match="negativo"):
        c.saldo = -5
    assert c.saldo == 100


def test_p4_heranca_sobe_ate_quem_sobrescreveu():
    class Quarto:
        def preco_noite(self):
            return 200

        def descricao(self):
            return f"{self.__class__.__name__}: R$ {self.preco_noite()}"

    class Suite(Quarto):
        def preco_noite(self):
            return 500

    class Master(Suite):
        pass

    assert Master().descricao() == "Master: R$ 500"


def test_p5_adapter():
    repo = adapter.NeonReservaAdapter(adapter.ClienteNeon())
    a = repo.salvar({"h": "Ana"})
    b = repo.salvar({"h": "Bia"})
    assert (a, b, type(b).__name__) == (1, 2, "int")
    assert repo.buscar(3) is None


def test_p6_facade_ocupado_nao_gasta_id():
    notif = facade.Notificador()
    f = facade.RecepcaoFacade(facade.Disponibilidade([101]), facade.Tarifa(), facade.Reservas(), notif)
    assert f.reservar(101, "Ana", 2) == {"ok": False, "motivo": "indisponivel"}
    assert f.reservar(201, "Bia", 2) == {"ok": True, "reserva_id": 1, "total": 1000.0}
    assert len(notif.enviadas) == 1


def test_p7_viewmodel():
    painel = mvvm.PainelQuartosVM([
        {"numero": 1, "categoria": "c", "diaria": 99.5, "ocupado": True},
        {"numero": 2, "categoria": "c", "diaria": 100, "ocupado": True},
    ])
    assert painel.livres == 0
    assert painel.rodape == "LOTADO - nenhum quarto livre"
    assert painel.itens[0].preco_formatado == "R$ 99.50"


def test_p8_ordem_importa_com_desconto_percentual():
    ComDesconto10 = decorator.ComDescontoFidelidade
    a = ComDesconto10(decorator.ComTransfer(decorator.ReservaBase(100, 1)))
    b = decorator.ComTransfer(ComDesconto10(decorator.ReservaBase(100, 1)))
    assert (a.preco(), b.preco()) == (162.0, 170.0)
