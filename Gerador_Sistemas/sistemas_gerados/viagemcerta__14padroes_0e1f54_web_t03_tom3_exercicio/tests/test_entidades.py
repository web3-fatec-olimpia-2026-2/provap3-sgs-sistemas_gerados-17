"""Testes da Viagcert (ENCAPSULAMENTO): regras, LIMITES e total calculado."""
import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.noites * obj.valor_noite, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.noites = obj.noites + 1
    assert obj.total == round(obj.noites * obj.valor_noite, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(viajante="  Elisa  ").viajante == "Elisa"


def test_observacao_sem_regra_aceita_qualquer_texto():
    assert criar().observacao == ""
    assert criar(observacao="qualquer coisa").observacao == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_viajante_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(viajante=invalido)


def test_viajante_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.viajante = ''
    assert obj.viajante == DADOS_EXEMPLO[0]["viajante"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", ['X'])
def test_viajante_valor_no_limite_e_aceito(limite):
    assert criar(viajante=limite).viajante == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_voo_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(voo=invalido)


def test_voo_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.voo = 0
    assert obj.voo == DADOS_EXEMPLO[0]["voo"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1])
def test_voo_valor_no_limite_e_aceito(limite):
    assert criar(voo=limite).voo == limite


@pytest.mark.parametrize("invalido", [0, 31, 2.5, '3', True, None])
def test_noites_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(noites=invalido)


def test_noites_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.noites = 0
    assert obj.noites == DADOS_EXEMPLO[0]["noites"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [1, 30])
def test_noites_valor_no_limite_e_aceito(limite):
    assert criar(noites=limite).noites == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_valor_noite_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(valor_noite=invalido)


def test_valor_noite_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.valor_noite = -0.01
    assert obj.valor_noite == DADOS_EXEMPLO[0]["valor_noite"]  # o valor válido foi preservado


@pytest.mark.parametrize("limite", [0.0])
def test_valor_noite_valor_no_limite_e_aceito(limite):
    assert criar(valor_noite=limite).valor_noite == limite
