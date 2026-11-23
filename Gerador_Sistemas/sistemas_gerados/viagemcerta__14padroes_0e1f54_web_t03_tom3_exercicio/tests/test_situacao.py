"""Testes do STATE: mesmo comportamento da escada de ifs; transições proibidas; estado novo."""
import pytest

from nucleo.antes_situacao import SituacaoAntiga
from nucleo.situacao import Confirmado, Estado, SituacaoViagcert, TransicaoInvalida
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


@pytest.mark.parametrize("acoes", SEQUENCIAS)
def test_mesmo_comportamento_da_escada_de_ifs(acoes):
    assert aplicar(SituacaoViagcert(criar()), acoes) == aplicar(SituacaoAntiga(criar()), acoes)


def test_fluxo_feliz():
    situacao = SituacaoViagcert(criar())
    situacao.confirmar()
    situacao.concluir()
    assert situacao.status == "concluido"


@pytest.mark.parametrize("acoes, proibida", [([], "concluir"), (["confirmar", "concluir"], "cancelar"),
                                             (["cancelar"], "confirmar")])
def test_transicao_proibida(acoes, proibida):
    situacao = SituacaoViagcert(criar())
    for acao in acoes:
        getattr(situacao, acao)()
    with pytest.raises(TransicaoInvalida):
        getattr(situacao, proibida)()


def test_estado_novo_sem_mudar_o_contexto():
    class EmEspera(Estado):
        nome = "em espera"

        def confirmar(self, contexto):
            contexto.estado = Confirmado()

    situacao = SituacaoViagcert(criar())
    situacao.estado = EmEspera()
    situacao.confirmar()
    assert situacao.status == "confirmado"
