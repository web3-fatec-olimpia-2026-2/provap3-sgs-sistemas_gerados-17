"""
Testes do Adapter.

A prova de que o Adapter funciona: o MESMO teste que vale para o
ArmazenamentoLocal passa a valer para o cliente Neon embrulhado no Adapter.
Para o servico, os dois viraram o mesmo tipo de coisa (ReservaRepository).

Rode:   python3 -m pytest -v
"""
import pytest
from reservas import (
    ReservaRepository,
    ArmazenamentoLocal,
    ClienteNeon,
    NeonReservaAdapter,
    ReservaService,
)

UMA_RESERVA = {"quarto": 101, "hospede": "Ana", "noites": 3}


# --- o Adapter respeita o contrato ReservaRepository -----------------------
def test_adapter_e_um_reserva_repository():
    adapter = NeonReservaAdapter(ClienteNeon())
    assert isinstance(adapter, ReservaRepository)


def test_adapter_salvar_devolve_id_inteiro():
    adapter = NeonReservaAdapter(ClienteNeon())
    novo_id = adapter.salvar(UMA_RESERVA)
    assert isinstance(novo_id, int)
    assert novo_id == 1


def test_adapter_buscar_devolve_a_reserva_salva():
    adapter = NeonReservaAdapter(ClienteNeon())
    novo_id = adapter.salvar(UMA_RESERVA)
    assert adapter.buscar(novo_id) == UMA_RESERVA


def test_adapter_buscar_inexistente_devolve_none():
    adapter = NeonReservaAdapter(ClienteNeon())
    assert adapter.buscar(999) is None


# --- a prova da substituibilidade: local e adapter sao intercambiaveis ------
@pytest.mark.parametrize(
    "repo",
    [ArmazenamentoLocal(), NeonReservaAdapter(ClienteNeon())],
    ids=["local", "neon_adapter"],
)
def test_qualquer_repo_salva_e_busca_igual(repo):
    novo_id = repo.salvar(UMA_RESERVA)
    assert repo.buscar(novo_id) == UMA_RESERVA


# --- com o Adapter, o servico nao precisa mais do 'if de banco' ------------
def test_servico_funciona_com_qualquer_repo_sem_flag():
    # O objetivo final: ReservaService recebendo UM repo so.
    # Depois da refatoracao, o professor remove o 'if usa_neon' e passa a
    # aceitar qualquer ReservaRepository. Este teste trava o comportamento.
    repo = NeonReservaAdapter(ClienteNeon())
    service = ReservaService(repo_local=repo, cliente_neon=None, usa_neon=False)
    novo_id = service.confirmar(UMA_RESERVA)
    assert novo_id == 1
    assert repo.buscar(novo_id) == UMA_RESERVA
