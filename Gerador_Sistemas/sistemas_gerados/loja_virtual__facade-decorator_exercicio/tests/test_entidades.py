"""Testes da Pedido (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.quantidade * obj.preco_unitario, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.quantidade = obj.quantidade + 1
    assert obj.total == round(obj.quantidade * obj.preco_unitario, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(cliente="  Juliana  ").cliente == "Juliana"


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
def test_produto_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(produto=invalido)


def test_produto_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.produto = 0
    assert obj.produto == DADOS_EXEMPLO[0]["produto"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_produto_valor_no_limite_e_aceito(limite):
    assert criar(produto=limite).produto == limite


@pytest.mark.parametrize("invalido", [0, 51, 2.5, '3', True, None])
def test_quantidade_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(quantidade=invalido)


def test_quantidade_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.quantidade = 0
    assert obj.quantidade == DADOS_EXEMPLO[0]["quantidade"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 50])
def test_quantidade_valor_no_limite_e_aceito(limite):
    assert criar(quantidade=limite).quantidade == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_preco_unitario_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(preco_unitario=invalido)


def test_preco_unitario_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.preco_unitario = -0.01
    assert obj.preco_unitario == DADOS_EXEMPLO[0]["preco_unitario"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_preco_unitario_valor_no_limite_e_aceito(limite):
    assert criar(preco_unitario=limite).preco_unitario == limite
