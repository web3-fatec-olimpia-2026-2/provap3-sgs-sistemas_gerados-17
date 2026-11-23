import pytest

from nucleo.situacao import Confirmado, Estado, SituacaoIngresso, TransicaoInvalida
from tests.fabrica import criar

SEQUENCIAS = [[], ["confirmar"], ["confirmar", "concluir"], ["cancelar"], ["confirmar", "cancelar"],
              ["concluir"], ["confirmar", "concluir", "cancelar"], ["cancelar", "confirmar"]]


def aplicar(situacao, acoes):
    for acao in acoes:
        try:
            getattr(situacao, acao)()
        except (TransicaoInvalida, ValueError):
            return f"erro em {acao}"
    return situacao.status


def test_fluxo_feliz():
    situacao = SituacaoIngresso(criar())
    situacao.confirmar()
    situacao.concluir()
    assert situacao.status == "concluido"


@pytest.mark.parametrize("acoes, proibida", [([], "concluir"), (["confirmar", "concluir"], "cancelar"),
                                             (["cancelar"], "confirmar")])
def test_transicao_proibida(acoes, proibida):
    situacao = SituacaoIngresso(criar())
    for acao in acoes:
        getattr(situacao, acao)()
    with pytest.raises(TransicaoInvalida):
        getattr(situacao, proibida)()


def test_estado_novo_sem_mudar_o_contexto():
    class EmEspera(Estado):
        nome = "em espera"

        def confirmar(self, contexto):
            contexto.estado = Confirmado()

    situacao = SituacaoIngresso(criar())
    situacao.estado = EmEspera()
    situacao.confirmar()
    assert situacao.status == "confirmado"
