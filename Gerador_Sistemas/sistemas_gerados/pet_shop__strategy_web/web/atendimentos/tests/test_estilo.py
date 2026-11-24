"""Testes do ESTILO "simples": páginas com os estáticos certos e sem estilo/script inline (CSP)."""
import re

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse

ESTATICOS = ['atendimentos/js/app.js']
NOTAS = False


@pytest.mark.django_db
@pytest.mark.parametrize("rota", ["atendimentos:lista", "atendimentos:criar"])
def test_pagina_usa_os_estaticos_do_estilo(client, rota):
    html = client.get(reverse(rota)).content.decode()
    for caminho in ESTATICOS:
        assert caminho in html
        assert finders.find(caminho), caminho


@pytest.mark.django_db
@pytest.mark.parametrize("rota", ["atendimentos:lista", "atendimentos:criar"])
def test_sem_estilo_nem_script_inline(client, rota):
    html = client.get(reverse(rota)).content.decode()
    assert "style=" not in html and "onclick=" not in html
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)


@pytest.mark.django_db
def test_notas_de_apresentacao(client):
    html = client.get(reverse("atendimentos:lista")).content.decode()
    assert ("data-apresentacao" in html) is NOTAS
    assert ("data-alternar-apresentacao" in html) is NOTAS
