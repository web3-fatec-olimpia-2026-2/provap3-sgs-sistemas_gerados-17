"""Página de exercícios (modo exercício): questionário com a resposta oculta atrás de "Ver resposta"."""
import re

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_pagina_de_exercicios_mostra_o_questionario(client):
    resposta = client.get(reverse("pharns:exercicios"))
    assert resposta.status_code == 200
    html = resposta.content.decode()
    assert html.count("<details") == 141                 # uma resposta oculta por pergunta
    assert html.count(">Ver resposta</summary>") == 141
    assert "style=" not in html and "onclick" not in html.lower()
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)   # nenhum script inline (CSP)


@pytest.mark.django_db
def test_lista_tem_link_para_os_exercicios(client):
    html = client.get(reverse("pharns:lista")).content.decode()
    assert reverse("pharns:exercicios") in html
