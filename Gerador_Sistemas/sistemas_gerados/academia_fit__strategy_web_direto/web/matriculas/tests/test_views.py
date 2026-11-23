"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from matriculas.models import Matricula


def form_data(**mudancas):
    copia = {"aluno": "Fernanda", "turma": "101", "meses": "2", "mensalidade": "100.00", "objetivo": "", "tipo": "mensal"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("matriculas:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("matriculas:criar"), form_data())
    assert resposta.status_code == 302
    assert Matricula.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("matriculas:criar"), form_data(meses="0"))
    assert resposta.status_code == 200
    assert Matricula.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("matriculas:criar"), form_data(tipo="universitario"))
    html = client.get(reverse("matriculas:lista")).content.decode()
    assert "R$ 140.00" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("matriculas:criar"), form_data())
    dados = client.get(reverse("matriculas:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 200.00"
