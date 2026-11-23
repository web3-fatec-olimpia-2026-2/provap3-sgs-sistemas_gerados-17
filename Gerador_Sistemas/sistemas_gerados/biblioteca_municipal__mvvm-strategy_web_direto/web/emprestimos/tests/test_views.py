"""Testes das VIEWS (MVT): finas — delegam ao Service e ao ViewModel."""
import pytest
from django.urls import reverse

from emprestimos.models import Emprestimo


def form_data(**mudancas):
    copia = {"leitor": "Beatriz", "exemplar": "101", "dias": "2", "taxa_dia": "2.50", "observacao": "", "tipo": "comum"}
    copia.update(mudancas)
    return copia


@pytest.mark.django_db
def test_lista_vazia(client):
    resposta = client.get(reverse("emprestimos:lista"))
    assert resposta.status_code == 200
    assert "Nenhum registro ainda" in resposta.content.decode()


@pytest.mark.django_db
def test_criar_valido_salva_e_redireciona(client):
    resposta = client.post(reverse("emprestimos:criar"), form_data())
    assert resposta.status_code == 302
    assert Emprestimo.objects.count() == 1


@pytest.mark.django_db
def test_criar_invalido_nao_salva(client):
    resposta = client.post(reverse("emprestimos:criar"), form_data(dias="0"))
    assert resposta.status_code == 200
    assert Emprestimo.objects.count() == 0


@pytest.mark.django_db
def test_lista_mostra_o_valor_com_a_politica(client):
    client.post(reverse("emprestimos:criar"), form_data(tipo="estudante"))
    html = client.get(reverse("emprestimos:lista")).content.decode()
    assert "R$ 2.50" in html


@pytest.mark.django_db
def test_api_devolve_json(client):
    client.post(reverse("emprestimos:criar"), form_data())
    dados = client.get(reverse("emprestimos:api")).json()
    assert len(dados["itens"]) == 1 and dados["total"] == "R$ 5.00"
