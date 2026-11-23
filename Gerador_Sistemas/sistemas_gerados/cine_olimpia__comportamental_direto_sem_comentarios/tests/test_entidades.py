import pytest

from tests.fabrica import DADOS_EXEMPLO, criar, itens_exemplo


def test_cria_com_dados_validos():
    obj = criar()
    for campo, valor in DADOS_EXEMPLO[0].items():
        assert getattr(obj, campo) == valor


def test_total_e_quantidade_vezes_preco():
    for obj in itens_exemplo():
        assert obj.total == round(obj.quantidade * obj.preco, 2)


def test_total_acompanha_mudanca():
    obj = criar()
    obj.quantidade = obj.quantidade + 1
    assert obj.total == round(obj.quantidade * obj.preco, 2)


def test_total_e_somente_leitura():
    with pytest.raises(AttributeError):
        criar().total = 1


def test_texto_obrigatorio_e_guardado_sem_espacos():
    assert criar(espectador="  Natália  ").espectador == "Natália"


def test_poltrona_sem_regra_aceita_qualquer_texto():
    assert criar().poltrona == ""
    assert criar(poltrona="qualquer coisa").poltrona == "qualquer coisa"


@pytest.mark.parametrize("invalido", ['', '   ', 123, None])
def test_espectador_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(espectador=invalido)


def test_espectador_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.espectador = ''
    assert obj.espectador == DADOS_EXEMPLO[0]["espectador"]


@pytest.mark.parametrize("limite", ['X'])
def test_espectador_valor_no_limite_e_aceito(limite):
    assert criar(espectador=limite).espectador == limite


@pytest.mark.parametrize("invalido", [0, -9, 2.5, '3', True, None])
def test_sessao_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(sessao=invalido)


def test_sessao_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.sessao = 0
    assert obj.sessao == DADOS_EXEMPLO[0]["sessao"]


@pytest.mark.parametrize("limite", [1])
def test_sessao_valor_no_limite_e_aceito(limite):
    assert criar(sessao=limite).sessao == limite


@pytest.mark.parametrize("invalido", [0, 11, 2.5, '3', True, None])
def test_quantidade_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(quantidade=invalido)


def test_quantidade_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.quantidade = 0
    assert obj.quantidade == DADOS_EXEMPLO[0]["quantidade"]


@pytest.mark.parametrize("limite", [1, 10])
def test_quantidade_valor_no_limite_e_aceito(limite):
    assert criar(quantidade=limite).quantidade == limite


@pytest.mark.parametrize("invalido", [-0.01, -10, '10', True, None])
def test_preco_invalido_e_barrado_na_criacao(invalido):
    with pytest.raises(ValueError):
        criar(preco=invalido)


def test_preco_invalido_e_barrado_na_alteracao():
    obj = criar()
    with pytest.raises(ValueError):
        obj.preco = -0.01
    assert obj.preco == DADOS_EXEMPLO[0]["preco"]


@pytest.mark.parametrize("limite", [0.0])
def test_preco_valor_no_limite_e_aceito(limite):
    assert criar(preco=limite).preco == limite
