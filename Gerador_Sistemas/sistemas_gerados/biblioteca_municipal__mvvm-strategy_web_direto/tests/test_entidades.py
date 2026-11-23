"""Testes da Emprestimo (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.dias * obj.taxa_dia, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.dias = obj.dias + 1
    assert obj.total == round(obj.dias * obj.taxa_dia, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(leitor="  Beatriz  ").leitor == "Beatriz"


def test_observacao_sem_regra_aceita_qualquer_texto():
    assert criar().observacao == ""
    assert criar(observacao="qualquer coisa").observacao == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_leitor_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(leitor=invalido)


def test_leitor_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.leitor = ''
    assert obj.leitor == DADOS_EXEMPLO[0]["leitor"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_leitor_valor_no_limite_e_aceito(limite):
    assert criar(leitor=limite).leitor == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_exemplar_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(exemplar=invalido)


def test_exemplar_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.exemplar = 0
    assert obj.exemplar == DADOS_EXEMPLO[0]["exemplar"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_exemplar_valor_no_limite_e_aceito(limite):
    assert criar(exemplar=limite).exemplar == limite


@pytest.mark.parametrize("invalido", [0, 31, 2.5, '3', True, None])
def test_dias_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(dias=invalido)


def test_dias_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.dias = 0
    assert obj.dias == DADOS_EXEMPLO[0]["dias"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 30])
def test_dias_valor_no_limite_e_aceito(limite):
    assert criar(dias=limite).dias == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_taxa_dia_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(taxa_dia=invalido)


def test_taxa_dia_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.taxa_dia = -0.01
    assert obj.taxa_dia == DADOS_EXEMPLO[0]["taxa_dia"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_taxa_dia_valor_no_limite_e_aceito(limite):
    assert criar(taxa_dia=limite).taxa_dia == limite
