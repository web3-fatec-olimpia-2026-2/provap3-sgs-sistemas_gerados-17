"""Testes do PWA: manifest (janela de app), service worker na raiz, ícones e páginas apontando para eles."""
import json

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse


def test_manifest_abre_como_app(client):
    resposta = client.get("/manifest.webmanifest")
    dados = json.loads(resposta.content)
    assert resposta.status_code == 200 and resposta["Content-Type"].startswith("application/manifest+json")
    assert dados["display"] == "standalone" and dados["start_url"] == "/"
    assert {icone["sizes"] for icone in dados["icons"]} == {"192x192", "512x512"}


def test_service_worker_na_raiz(client):
    resposta = client.get("/sw.js")
    assert resposta.status_code == 200 and "javascript" in resposta["Content-Type"]
    assert resposta["Service-Worker-Allowed"] == "/" and "fetch" in resposta.content.decode()


@pytest.mark.parametrize("tamanho", [192, 512])
def test_icones_sao_png(tamanho):
    with open(finders.find(f"pharns/icone-{tamanho}.png"), "rb") as arquivo:
        assert arquivo.read(8) == b"\x89PNG\r\n\x1a\n"


@pytest.mark.django_db
@pytest.mark.parametrize("rota", ["pharns:lista", "pharns:criar"])
def test_paginas_apontam_para_o_manifest(client, rota):
    html = client.get(reverse(rota)).content.decode()
    assert 'rel="manifest"' in html and "js/app.js" in html


def test_app_js_registra_o_service_worker():
    with open(finders.find("pharns/js/app.js"), encoding="utf-8") as arquivo:
        assert "serviceWorker" in arquivo.read()
