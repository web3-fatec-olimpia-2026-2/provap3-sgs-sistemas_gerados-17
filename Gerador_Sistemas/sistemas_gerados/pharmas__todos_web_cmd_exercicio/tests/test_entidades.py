"""Testes da Pharm (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
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


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_produto_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(produto=invalido)


def test_produto_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.produto = ''
    assert obj.produto == DADOS_EXEMPLO[0]["produto"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_produto_valor_no_limite_e_aceito(limite):
    assert criar(produto=limite).produto == limite


@pytest.mark.parametrize("invalido", [-1, 131, 2.5, '3', True, None])
def test_idade_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(idade=invalido)


def test_idade_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.idade = -1
    assert obj.idade == DADOS_EXEMPLO[0]["idade"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0, 130])
def test_idade_valor_no_limite_e_aceito(limite):
    assert criar(idade=limite).idade == limite


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_categoria_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(categoria=invalido)


def test_categoria_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.categoria = ''
    assert obj.categoria == DADOS_EXEMPLO[0]["categoria"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_categoria_valor_no_limite_e_aceito(limite):
    assert criar(categoria=limite).categoria == limite


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_cosmeticos_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(cosmeticos=invalido)


def test_cosmeticos_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.cosmeticos = ''
    assert obj.cosmeticos == DADOS_EXEMPLO[0]["cosmeticos"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_cosmeticos_valor_no_limite_e_aceito(limite):
    assert criar(cosmeticos=limite).cosmeticos == limite


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_medicamentos_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(medicamentos=invalido)


def test_medicamentos_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.medicamentos = ''
    assert obj.medicamentos == DADOS_EXEMPLO[0]["medicamentos"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_medicamentos_valor_no_limite_e_aceito(limite):
    assert criar(medicamentos=limite).medicamentos == limite
