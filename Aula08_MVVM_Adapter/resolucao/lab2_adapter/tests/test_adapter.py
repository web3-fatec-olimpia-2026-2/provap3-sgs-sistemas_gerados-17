"""Lab 2 Adapter — 7 testes ORIGINAIS (6 funções, 1 parametrizada 2x) + os meus."""
import pytest

from reservas import (ArmazenamentoLocal, ClienteNeon, NeonReservaAdapter,
                      ReservaRepository, ReservaService, ReservaServiceLimpo)

UMA_RESERVA = {"quarto": 101, "hospede": "Ana", "noites": 3}


# --- originais ---
def test_adapter_e_um_reserva_repository():
    assert isinstance(NeonReservaAdapter(ClienteNeon()), ReservaRepository)


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
    assert NeonReservaAdapter(ClienteNeon()).buscar(999) is None


@pytest.mark.parametrize(
    "repo",
    [ArmazenamentoLocal(), NeonReservaAdapter(ClienteNeon())],
    ids=["local", "neon_adapter"],
)
def test_qualquer_repo_salva_e_busca_igual(repo):
    novo_id = repo.salvar(UMA_RESERVA)
    assert repo.buscar(novo_id) == UMA_RESERVA


def test_servico_funciona_com_qualquer_repo_sem_flag():
    repo = NeonReservaAdapter(ClienteNeon())
    service = ReservaService(repo_local=repo, cliente_neon=None, usa_neon=False)
    novo_id = service.confirmar(UMA_RESERVA)
    assert novo_id == 1
    assert repo.buscar(novo_id) == UMA_RESERVA


# --- meus: o serviço limpo, sem if de banco ---
@pytest.fixture(params=["local", "neon"])
def repo(request):
    # A MESMA bateria de testes roda para os dois bancos → substituibilidade.
    return ArmazenamentoLocal() if request.param == "local" else NeonReservaAdapter(ClienteNeon())


def test_servico_limpo_confirma_e_consulta(repo):
    svc = ReservaServiceLimpo(repo)
    novo_id = svc.confirmar(UMA_RESERVA)
    assert svc.consultar(novo_id) == UMA_RESERVA


def test_servico_limpo_aplica_regra_sem_saber_o_banco(repo):
    with pytest.raises(ValueError):
        ReservaServiceLimpo(repo).confirmar({"quarto": 1, "hospede": "X", "noites": 0})


def test_adapter_nao_vaza_formato_do_neon():
    adapter = NeonReservaAdapter(ClienteNeon())
    novo_id = adapter.salvar(UMA_RESERVA)
    devolvido = adapter.buscar(novo_id)
    assert "found" not in devolvido and "row" not in devolvido   # desembrulhado
