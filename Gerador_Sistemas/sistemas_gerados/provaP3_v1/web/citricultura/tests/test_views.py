"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from citricultura.models import LoteCitros


def form_data(**mudancas):
    copia = {"cooperado": "Isabela", "talhao": "101", "caixas": "2", "preco_caixa": "38.00", "observacao": "", "tipo": "industria"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("citricultura:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("citricultura:criar"), form_data())
    assert resposta.status_code == 302
    assert LoteCitros.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("citricultura:criar"), form_data(caixas="0"))
    assert resposta.status_code == 200
    assert LoteCitros.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("citricultura:criar"), form_data(tipo="mesa"))
    html = client.get(reverse("citricultura:lista")).content.decode()
    assert "R$ 95.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("citricultura:criar"), form_data())
    dados = client.get(reverse("citricultura:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 76.00"


# ---------------------------------------------------------------- CRUD: detalhe, editar e excluir
def criado(client):
    client.post(reverse("citricultura:criar"), form_data())
    return LoteCitros.objects.get()


@pytest.mark.django_db
def test_detalhe_mostra_o_registro(client):
    obj = criado(client)
    html = client.get(reverse("citricultura:detalhe", args=[obj.pk])).content.decode()
    assert str(obj.cooperado) in html and "Valor final" in html


@pytest.mark.django_db
def test_editar_altera_o_registro(client):
    obj = criado(client)
    resposta = client.post(reverse("citricultura:editar", args=[obj.pk]), form_data(caixas="3"))
    assert resposta.status_code == 302
    obj.refresh_from_db()
    assert obj.caixas == 3


@pytest.mark.django_db
def test_editar_invalido_nao_altera(client):
    obj = criado(client)
    antes = obj.caixas
    resposta = client.post(reverse("citricultura:editar", args=[obj.pk]), form_data(caixas="0"))
    assert resposta.status_code == 200
    obj.refresh_from_db()
    assert obj.caixas == antes


@pytest.mark.django_db
def test_excluir_so_com_post(client):
    obj = criado(client)
    assert client.get(reverse("citricultura:excluir", args=[obj.pk])).status_code == 200   # GET só confirma
    assert LoteCitros.objects.count() == 1
    assert client.post(reverse("citricultura:excluir", args=[obj.pk])).status_code == 302
    assert LoteCitros.objects.count() == 0


@pytest.mark.django_db
def test_registro_inexistente_da_404(client):
    obj = criado(client)
    pk = obj.pk
    obj.delete()
    for rota in ("citricultura:detalhe", "citricultura:editar", "citricultura:excluir"):
        assert client.get(reverse(rota, args=[pk])).status_code == 404
