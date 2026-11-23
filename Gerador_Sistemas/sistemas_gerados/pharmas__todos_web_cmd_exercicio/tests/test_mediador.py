"""Testes do MEDIATOR: o mediador coordena; os componentes só conhecem o mediador."""
import pytest

from nucleo.antes_mediador import BotaoAntigo, CampoAntigo, ResumoAntigo, SeletorAntigo
from nucleo.mediador import FATORES, FormularioMediador
from tests.fabrica import DADOS_EXEMPLO

PRECO = DADOS_EXEMPLO[0]["valor_unitario"]


def test_comeca_valido_com_um():
    form = FormularioMediador(PRECO)
    assert form.botao.habilitado and form.resumo.texto.startswith("1 ")


@pytest.mark.parametrize("qtd", [1, 2, 3])
def test_digitar_recalcula_o_resumo(qtd):
    form = FormularioMediador(PRECO)
    form.quantidade.digitar(qtd)
    assert form.resumo.texto.endswith(f"R$ {round(qtd * PRECO * FATORES['comum'], 2):.2f}")


def test_valor_invalido_desliga_o_botao():
    form = FormularioMediador(PRECO)
    form.quantidade.digitar(0)
    assert not form.botao.habilitado and "inválido" in form.resumo.texto


def test_trocar_o_tipo_aplica_o_fator():
    form = FormularioMediador(PRECO)
    form.quantidade.digitar(2)
    form.tipo.escolher("especial")
    assert form.resumo.texto.endswith(f"R$ {round(2 * PRECO * FATORES['especial'], 2):.2f}")


def test_componentes_so_conhecem_o_mediador():
    form = FormularioMediador(PRECO)
    for componente in (form.quantidade, form.tipo, form.resumo, form.botao):
        ligados = [valor for valor in vars(componente).values() if hasattr(valor, "__dict__")]
        assert ligados == [form]


@pytest.mark.parametrize("qtd", [0, 1, 3])
def test_mesmo_resultado_da_versao_acoplada(qtd):
    seletor, resumo, botao = SeletorAntigo(), ResumoAntigo(), BotaoAntigo()
    CampoAntigo(PRECO, seletor, resumo, botao).digitar(qtd)
    form = FormularioMediador(PRECO)
    form.quantidade.digitar(qtd)
    assert (form.resumo.texto, form.botao.habilitado) == (resumo.texto, botao.habilitado)
