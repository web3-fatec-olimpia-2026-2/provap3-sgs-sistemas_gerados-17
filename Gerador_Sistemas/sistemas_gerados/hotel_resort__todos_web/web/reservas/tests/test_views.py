"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from reservas.models import Reserva


def form_data(**mudancas):
    copia = {"hospede": "Ana", "quarto": "101", "diarias": "2", "valor_diaria": "200.00", "observacao": "", "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("reservas:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("reservas:criar"), form_data())
    assert resposta.status_code == 302
    assert Reserva.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("reservas:criar"), form_data(diarias="0"))
    assert resposta.status_code == 200
    assert Reserva.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("reservas:criar"), form_data(tipo="fidelidade"))
    html = client.get(reverse("reservas:lista")).content.decode()
    assert "R$ 360.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("reservas:criar"), form_data())
    dados = client.get(reverse("reservas:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 400.00"
