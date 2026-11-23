"""Testes do BUILDER: monta o mesmo que o construtor, avisa o que falta e encadeia."""
import pytest

from destinos.nucleo.antes_construtor import nova_destino_antiga
from destinos.nucleo.construtor import DiretorDeDestino, DestinoBuilder
from destinos.tests.nucleo.fabrica import DADOS_EXEMPLO


def construir_com(dados):
    builder = DestinoBuilder()
    for campo, valor in dados.items():
        getattr(builder, f"com_{campo}")(valor)
    return builder.construir()


@pytest.mark.parametrize("indice", range(4))
def test_builder_monta_os_mesmos_valores(indice):
    dados = DADOS_EXEMPLO[indice]
    feito = construir_com(dados)
    for campo, valor in dados.items():
        assert getattr(feito, campo) == valor


@pytest.mark.parametrize("indice", range(4))
def test_igual_a_versao_posicional(indice):
    dados = DADOS_EXEMPLO[indice]
    antigo = nova_destino_antiga(*dados.values())
    assert vars(construir_com(dados)) == vars(antigo)


def test_interface_fluente_devolve_o_proprio_builder():
    builder = DestinoBuilder()
    assert builder.com_cliente("Ana") is builder


def test_falta_campo_obrigatorio_diz_qual():
    with pytest.raises(ValueError, match="quantidade"):
        DestinoBuilder().com_cliente("Ana").construir()


def test_valor_invalido_e_barrado_pela_entidade():
    with pytest.raises(ValueError):
        construir_com(dict(DADOS_EXEMPLO[0], quantidade=0))


def test_diretor_monta_a_receita_padrao():
    obj = DiretorDeDestino().basico("Ana")
    assert obj.cliente == "Ana" and obj.total >= 0


def test_ordem_dos_passos_nao_importa():
    dados = DADOS_EXEMPLO[1]
    invertido = dict(reversed(list(dados.items())))
    assert vars(construir_com(invertido)) == vars(construir_com(dados))
