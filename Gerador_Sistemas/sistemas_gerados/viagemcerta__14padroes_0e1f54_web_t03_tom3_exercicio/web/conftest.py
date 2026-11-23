"""Testes com o baseline de segurança: o cliente de testes fala HTTP, então sem redirecionar para HTTPS."""
import pytest


@pytest.fixture(autouse=True)
def _sem_https_nos_testes(settings):
    settings.SECURE_SSL_REDIRECT = False
