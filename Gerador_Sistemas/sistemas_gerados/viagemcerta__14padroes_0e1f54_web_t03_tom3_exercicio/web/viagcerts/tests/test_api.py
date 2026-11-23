"""Testes da API REST: o mesmo ModelForm valida as telas e a API; o settings da app manda nos limites."""
import json

import pytest
from django.test import Client, override_settings
from django.urls import reverse

from viagcerts.models import Viagcert

pytestmark = pytest.mark.django_db
VALIDO = {"viajante": "Elisa", "voo": 101, "noites": 2, "valor_noite": "350.00", "observacao": "", "tipo": "comum"}


@pytest.fixture(autouse=True)
def api_no_padrao(settings):
    """Estes testes conferem o PADRÃO: o que o projeto escolheu no sgs api config não muda o resultado deles."""
    settings.VIAGCERTS_API_CAMPOS = {}


def enviar(client, metodo, url, dados):
    return getattr(client, metodo)(url, data=json.dumps(dados), content_type="application/json")


def colecao():
    return reverse("viagcerts:api_colecao")


def test_post_cria_e_get_lista(client):
    resposta = enviar(client, "post", colecao(), VALIDO)
    assert resposta.status_code == 201
    criado = resposta.json()
    assert criado["viajante"] == VALIDO["viajante"] and "total" in criado and "valor_final" in criado
    lista = client.get(colecao()).json()
    assert lista["total_registros"] == 1 and lista["itens"][0]["id"] == criado["id"]


def test_post_invalido_devolve_400_com_os_erros(client):
    resposta = enviar(client, "post", colecao(), {**VALIDO, "noites": 0})
    assert resposta.status_code == 400 and "noites" in resposta.json()["erros"]
    assert Viagcert.objects.count() == 0


def test_get_put_patch_delete_de_um_registro(client):
    criado = enviar(client, "post", colecao(), VALIDO).json()
    url = reverse("viagcerts:api_item", args=[criado["id"]])
    assert client.get(url).json()["id"] == criado["id"]
    parcial = enviar(client, "patch", url, {"noites": 2})           # PATCH: só o campo enviado muda
    assert parcial.status_code == 200 and parcial.json()["noites"] == 2
    assert parcial.json()["viajante"] == VALIDO["viajante"]
    inteiro = enviar(client, "put", url, {**VALIDO, "noites": 3})   # PUT: o registro inteiro
    assert inteiro.status_code == 200 and inteiro.json()["noites"] == 3
    assert enviar(client, "put", url, {**VALIDO, "noites": 0}).status_code == 400
    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404


def test_metodo_nao_permitido_e_json_invalido(client):
    assert client.delete(colecao()).status_code == 405
    assert client.post(colecao(), data="{isto não é json", content_type="application/json").status_code == 400


def test_api_so_leitura_pelo_settings_da_app(client):
    with override_settings(VIAGCERTS_API_ESCRITA=False):
        assert enviar(client, "post", colecao(), VALIDO).status_code == 405
        assert client.get(colecao()).status_code == 200


def test_limite_da_lista_vem_do_settings_da_app(client):
    for _ in range(3):
        enviar(client, "post", colecao(), VALIDO)
    with override_settings(VIAGCERTS_API_LIMITE=2):
        dados = client.get(colecao()).json()
    assert len(dados["itens"]) == 2 and dados["total_registros"] == 3
    assert len(client.get(colecao(), {"limite": 1}).json()["itens"]) == 1


def test_csrf_continua_valendo_na_api():
    """Sem o token CSRF, escrever é recusado (403): a API não abre uma porta nos fundos."""
    assert enviar(Client(enforce_csrf_checks=True), "post", colecao(), VALIDO).status_code == 403


# ---------------------------------------------------------------- campos de cada endpoint (sgs api config)
def test_campos_de_cada_endpoint_vem_do_settings(client):
    enviar(client, "post", colecao(), VALIDO)
    padrao = client.get(colecao()).json()["itens"][0]
    assert "viajante" in padrao and "valor_final" in padrao and "titulo" not in padrao
    resumo = client.get(reverse("viagcerts:api")).json()["itens"][0]
    assert set(resumo) == {"id", "codigo", "titulo", "valor"}           # o resumo do painel (link "API")
    escolha = {"v1": {"viajante": False, "titulo": True}, "resumo": {"noites": True, "codigo": False}}
    with override_settings(VIAGCERTS_API_CAMPOS=escolha):
        item = client.get(colecao()).json()["itens"][0]
        assert "viajante" not in item and "titulo" in item
        resumo = client.get(reverse("viagcerts:api")).json()["itens"][0]
        assert resumo["noites"] == VALIDO["noites"] and "codigo" not in resumo
        campos = client.get(reverse("viagcerts:api_campos")).json()
        assert "viajante" in campos["disponiveis"] and "viajante" not in campos["expostos"]["v1"]


def test_quem_chama_escolhe_entre_os_campos_expostos(client):
    criado = enviar(client, "post", colecao(), VALIDO).json()
    item = client.get(colecao(), {"campos": "viajante,total"}).json()["itens"][0]
    assert set(item) == {"viajante", "total"}
    um = client.get(reverse("viagcerts:api_item", args=[criado["id"]]), {"campos": "id"}).json()
    assert um == {"id": criado["id"]}
    with override_settings(VIAGCERTS_API_CAMPOS={"v1": {"total": False}}):   # oculto não volta nem pedindo
        assert set(client.get(colecao(), {"campos": "viajante,total"}).json()["itens"][0]) == {"viajante"}
