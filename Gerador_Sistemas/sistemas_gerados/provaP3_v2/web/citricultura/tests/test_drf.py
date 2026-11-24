"""Testes da API do DRF com o APIClient (rest_framework.test): CRUD, validação (400) e o 404."""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from citricultura.models import LoteCitros

pytestmark = pytest.mark.django_db
VALIDO = {"cooperado": "Isabela", "talhao": 101, "caixas": 2, "preco_caixa": "38.00", "cidade": "Cidade 1", "observacao": "", "tipo": "industria"}


@pytest.fixture
def api():
    return APIClient()


def test_lista_vazia_e_post_cria(api):
    lista = reverse("lote_citros-list")
    assert api.get(lista).status_code == 200 and api.get(lista).json() == []
    resposta = api.post(lista, VALIDO, format="json")
    assert resposta.status_code == 201, resposta.json()
    assert resposta.json()["cooperado"] == VALIDO["cooperado"] and LoteCitros.objects.count() == 1


def test_post_invalido_devolve_400_com_o_campo(api):
    resposta = api.post(reverse("lote_citros-list"), {**VALIDO, "caixas": 0}, format="json")
    assert resposta.status_code == 400 and "caixas" in resposta.json()
    assert LoteCitros.objects.count() == 0


def test_get_patch_put_delete_de_um_registro(api):
    criado = api.post(reverse("lote_citros-list"), VALIDO, format="json").json()
    url = reverse("lote_citros-detail", args=[criado["id"]])
    assert api.get(url).json()["id"] == criado["id"]
    assert api.patch(url, {"caixas": 2}, format="json").json()["caixas"] == 2
    assert api.put(url, {**VALIDO, "caixas": 3}, format="json").json()["caixas"] == 3
    assert api.delete(url).status_code == 204
    assert api.get(url).status_code == 404


def test_a_raiz_da_api_lista_o_recurso(api):
    assert "lote-citroses" in api.get("/api/", HTTP_ACCEPT="application/json").json()
