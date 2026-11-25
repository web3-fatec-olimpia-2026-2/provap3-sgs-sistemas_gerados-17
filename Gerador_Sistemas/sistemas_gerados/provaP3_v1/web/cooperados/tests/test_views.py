"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from cooperados.models import Cooperado


def form_data(**mudancas):
    copia = {"cliente": "Ana", "codigo": "101", "quantidade": "2", "valor_unitario": "100.00", "observacao": "", "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("cooperados:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("cooperados:criar"), form_data())
    assert resposta.status_code == 302
    assert Cooperado.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("cooperados:criar"), form_data(quantidade="0"))
    assert resposta.status_code == 200
    assert Cooperado.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("cooperados:criar"), form_data(tipo="especial"))
    html = client.get(reverse("cooperados:lista")).content.decode()
    assert "R$ 180.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("cooperados:criar"), form_data())
    dados = client.get(reverse("cooperados:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 200.00"


# ---------------------------------------------------------------- CRUD: detalhe, editar e excluir
def criado(client):
    client.post(reverse("cooperados:criar"), form_data())
    return Cooperado.objects.get()


@pytest.mark.django_db
def test_detalhe_mostra_o_registro(client):
    obj = criado(client)
    html = client.get(reverse("cooperados:detalhe", args=[obj.pk])).content.decode()
    assert str(obj.cliente) in html and "Valor final" in html


@pytest.mark.django_db
def test_editar_altera_o_registro(client):
    obj = criado(client)
    resposta = client.post(reverse("cooperados:editar", args=[obj.pk]), form_data(quantidade="3"))
    assert resposta.status_code == 302
    obj.refresh_from_db()
    assert obj.quantidade == 3


@pytest.mark.django_db
def test_editar_invalido_nao_altera(client):
    obj = criado(client)
    antes = obj.quantidade
    resposta = client.post(reverse("cooperados:editar", args=[obj.pk]), form_data(quantidade="0"))
    assert resposta.status_code == 200
    obj.refresh_from_db()
    assert obj.quantidade == antes


@pytest.mark.django_db
def test_excluir_so_com_post(client):
    obj = criado(client)
    assert client.get(reverse("cooperados:excluir", args=[obj.pk])).status_code == 200   # GET só confirma
    assert Cooperado.objects.count() == 1
    assert client.post(reverse("cooperados:excluir", args=[obj.pk])).status_code == 302
    assert Cooperado.objects.count() == 0


@pytest.mark.django_db
def test_registro_inexistente_da_404(client):
    obj = criado(client)
    pk = obj.pk
    obj.delete()
    for rota in ("cooperados:detalhe", "cooperados:editar", "cooperados:excluir"):
        assert client.get(reverse(rota, args=[pk])).status_code == 404
