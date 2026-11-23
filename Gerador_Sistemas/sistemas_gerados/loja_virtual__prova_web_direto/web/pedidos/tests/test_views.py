"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from pedidos.models import Pedido


def form_data(**mudancas):
    copia = {"cliente": "Juliana", "produto": "101", "quantidade": "2", "preco_unitario": "50.00", "observacao": "", "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("pedidos:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("pedidos:criar"), form_data())
    assert resposta.status_code == 302
    assert Pedido.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("pedidos:criar"), form_data(quantidade="0"))
    assert resposta.status_code == 200
    assert Pedido.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("pedidos:criar"), form_data(tipo="fidelidade"))
    html = client.get(reverse("pedidos:lista")).content.decode()
    assert "R$ 90.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("pedidos:criar"), form_data())
    dados = client.get(reverse("pedidos:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 100.00"
