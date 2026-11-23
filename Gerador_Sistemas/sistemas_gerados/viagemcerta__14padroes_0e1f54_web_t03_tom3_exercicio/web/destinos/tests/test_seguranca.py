"""Testes do baseline de segurança (Instruções §12–14 e §22.1: cabeçalhos, cookies, CSP, admin)."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_cabecalhos_de_seguranca(client):
    resposta = client.get(reverse("destinos:lista"))
    assert resposta["X-Frame-Options"] == "DENY"
    assert resposta["X-Content-Type-Options"] == "nosniff"
    assert resposta["Referrer-Policy"] == "same-origin"
    assert resposta["Cross-Origin-Opener-Policy"] == "same-origin"
    politica = resposta.get("Content-Security-Policy-Report-Only") or resposta["Content-Security-Policy"]
    assert "default-src 'self'" in politica and "frame-ancestors 'none'" in politica


def test_cookies_e_limites(settings):
    assert settings.SESSION_COOKIE_HTTPONLY is True
    assert settings.SESSION_COOKIE_SAMESITE == settings.CSRF_COOKIE_SAMESITE == "Lax"
    assert settings.DATA_UPLOAD_MAX_MEMORY_SIZE == 1_048_576


@pytest.mark.django_db
def test_admin_fora_do_endereco_padrao(client, settings):
    assert settings.ADMIN_URL != "admin/"
    assert client.get("/admin/").status_code == 404


@pytest.mark.django_db
def test_get_nao_altera_estado(client):
    from destinos.models import Destino
    client.get(reverse("destinos:criar"))
    assert Destino.objects.count() == 0
