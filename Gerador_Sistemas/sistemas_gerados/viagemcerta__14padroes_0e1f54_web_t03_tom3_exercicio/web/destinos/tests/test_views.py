"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from destinos.models import Destino


def form_data(**mudancas):
    copia = {"cliente": "Ana", "codigo": "101", "quantidade": "2", "valor_unitario": "100.00", "cidade": "Cidade 1", "pais": "Pais 1", "observacao": "", "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("destinos:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("destinos:criar"), form_data())
    assert resposta.status_code == 302
    assert Destino.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("destinos:criar"), form_data(quantidade="0"))
    assert resposta.status_code == 200
    assert Destino.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("destinos:criar"), form_data(tipo="especial"))
    html = client.get(reverse("destinos:lista")).content.decode()
    assert "R$ 180.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("destinos:criar"), form_data())
    dados = client.get(reverse("destinos:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 200.00"


# ---------------------------------------------------------------- CRUD: detalhe, editar e excluir
def criado(client):
    client.post(reverse("destinos:criar"), form_data())
    return Destino.objects.get()


@pytest.mark.django_db
def test_detalhe_mostra_o_registro(client):
    obj = criado(client)
    html = client.get(reverse("destinos:detalhe", args=[obj.pk])).content.decode()
    assert str(obj.cliente) in html and "Valor final" in html


@pytest.mark.django_db
def test_editar_altera_o_registro(client):
    obj = criado(client)
    resposta = client.post(reverse("destinos:editar", args=[obj.pk]), form_data(quantidade="3"))
    assert resposta.status_code == 302
    obj.refresh_from_db()
    assert obj.quantidade == 3


@pytest.mark.django_db
def test_editar_invalido_nao_altera(client):
    obj = criado(client)
    antes = obj.quantidade
    resposta = client.post(reverse("destinos:editar", args=[obj.pk]), form_data(quantidade="0"))
    assert resposta.status_code == 200
    obj.refresh_from_db()
    assert obj.quantidade == antes


@pytest.mark.django_db
def test_excluir_so_com_post(client):
    obj = criado(client)
    assert client.get(reverse("destinos:excluir", args=[obj.pk])).status_code == 200   # GET só confirma
    assert Destino.objects.count() == 1
    assert client.post(reverse("destinos:excluir", args=[obj.pk])).status_code == 302
    assert Destino.objects.count() == 0


@pytest.mark.django_db
def test_registro_inexistente_da_404(client):
    obj = criado(client)
    pk = obj.pk
    obj.delete()
    for rota in ("destinos:detalhe", "destinos:editar", "destinos:excluir"):
        assert client.get(reverse(rota, args=[pk])).status_code == 404
