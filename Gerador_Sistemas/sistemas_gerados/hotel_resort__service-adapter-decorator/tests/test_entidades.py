"""Testes da Reserva (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.diarias * obj.valor_diaria, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.diarias = obj.diarias + 1
    assert obj.total == round(obj.diarias * obj.valor_diaria, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(hospede="  Ana  ").hospede == "Ana"


def test_observacao_sem_regra_aceita_qualquer_texto():
    assert criar().observacao == ""
    assert criar(observacao="qualquer coisa").observacao == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_hospede_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(hospede=invalido)


def test_hospede_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.hospede = ''
    assert obj.hospede == DADOS_EXEMPLO[0]["hospede"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_hospede_valor_no_limite_e_aceito(limite):
    assert criar(hospede=limite).hospede == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_quarto_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(quarto=invalido)


def test_quarto_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.quarto = 0
    assert obj.quarto == DADOS_EXEMPLO[0]["quarto"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_quarto_valor_no_limite_e_aceito(limite):
    assert criar(quarto=limite).quarto == limite


@pytest.mark.parametrize("invalido", [0, 31, 2.5, '3', True, None])
def test_diarias_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(diarias=invalido)


def test_diarias_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.diarias = 0
    assert obj.diarias == DADOS_EXEMPLO[0]["diarias"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 30])
def test_diarias_valor_no_limite_e_aceito(limite):
    assert criar(diarias=limite).diarias == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_valor_diaria_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(valor_diaria=invalido)


def test_valor_diaria_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.valor_diaria = -0.01
    assert obj.valor_diaria == DADOS_EXEMPLO[0]["valor_diaria"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_valor_diaria_valor_no_limite_e_aceito(limite):
    assert criar(valor_diaria=limite).valor_diaria == limite
