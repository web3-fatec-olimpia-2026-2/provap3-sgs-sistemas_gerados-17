"""Testes da Atendimento (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.quantidade * obj.valor_unitario, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.quantidade = obj.quantidade + 1
    assert obj.total == round(obj.quantidade * obj.valor_unitario, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(cliente="  Ana  ").cliente == "Ana"


def test_observacao_sem_regra_aceita_qualquer_texto():
    assert criar().observacao == ""
    assert criar(observacao="qualquer coisa").observacao == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_cliente_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(cliente=invalido)


def test_cliente_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.cliente = ''
    assert obj.cliente == DADOS_EXEMPLO[0]["cliente"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_cliente_valor_no_limite_e_aceito(limite):
    assert criar(cliente=limite).cliente == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_codigo_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(codigo=invalido)


def test_codigo_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.codigo = 0
    assert obj.codigo == DADOS_EXEMPLO[0]["codigo"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_codigo_valor_no_limite_e_aceito(limite):
    assert criar(codigo=limite).codigo == limite


@pytest.mark.parametrize("invalido", [0, 101, 2.5, '3', True, None])
def test_quantidade_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(quantidade=invalido)


def test_quantidade_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.quantidade = 0
    assert obj.quantidade == DADOS_EXEMPLO[0]["quantidade"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 100])
def test_quantidade_valor_no_limite_e_aceito(limite):
    assert criar(quantidade=limite).quantidade == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_valor_unitario_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(valor_unitario=invalido)


def test_valor_unitario_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.valor_unitario = -0.01
    assert obj.valor_unitario == DADOS_EXEMPLO[0]["valor_unitario"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_valor_unitario_valor_no_limite_e_aceito(limite):
    assert criar(valor_unitario=limite).valor_unitario == limite
