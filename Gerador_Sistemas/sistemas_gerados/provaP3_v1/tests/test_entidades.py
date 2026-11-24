"""Testes da LoteCitros (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.caixas * obj.preco_caixa, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.caixas = obj.caixas + 1
    assert obj.total == round(obj.caixas * obj.preco_caixa, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(cooperado="  Isabela  ").cooperado == "Isabela"


def test_observacao_sem_regra_aceita_qualquer_texto():
    assert criar().observacao == ""
    assert criar(observacao="qualquer coisa").observacao == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_cooperado_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(cooperado=invalido)


def test_cooperado_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.cooperado = ''
    assert obj.cooperado == DADOS_EXEMPLO[0]["cooperado"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_cooperado_valor_no_limite_e_aceito(limite):
    assert criar(cooperado=limite).cooperado == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_talhao_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(talhao=invalido)


def test_talhao_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.talhao = 0
    assert obj.talhao == DADOS_EXEMPLO[0]["talhao"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_talhao_valor_no_limite_e_aceito(limite):
    assert criar(talhao=limite).talhao == limite


@pytest.mark.parametrize("invalido", [0, 5001, 2.5, '3', True, None])
def test_caixas_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(caixas=invalido)


def test_caixas_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.caixas = 0
    assert obj.caixas == DADOS_EXEMPLO[0]["caixas"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 5000])
def test_caixas_valor_no_limite_e_aceito(limite):
    assert criar(caixas=limite).caixas == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_preco_caixa_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(preco_caixa=invalido)


def test_preco_caixa_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.preco_caixa = -0.01
    assert obj.preco_caixa == DADOS_EXEMPLO[0]["preco_caixa"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_preco_caixa_valor_no_limite_e_aceito(limite):
    assert criar(preco_caixa=limite).preco_caixa == limite
