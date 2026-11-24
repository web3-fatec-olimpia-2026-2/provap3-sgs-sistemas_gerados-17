"""Testes da preparação do site: comando garantir_admin, leitor de .env e tela de login do admin."""
import pytest
from django.contrib.auth import authenticate, get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from config.env import ler_env


@pytest.fixture
def credenciais(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "professor")
    monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "professor@exemplo.com")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "senha-de-teste-1")


@pytest.mark.django_db
def test_cria_o_superusuario(credenciais):
    call_command("garantir_admin")
    usuario = get_user_model().objects.get(username="professor")
    assert usuario.is_superuser and usuario.is_staff
    assert authenticate(username="professor", password="senha-de-teste-1") is not None


@pytest.mark.django_db
def test_rodar_de_novo_atualiza_a_senha(credenciais, monkeypatch):
    call_command("garantir_admin")
    monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "outra-senha-2")
    call_command("garantir_admin")
    assert get_user_model().objects.filter(username="professor").count() == 1
    assert authenticate(username="professor", password="outra-senha-2") is not None


@pytest.mark.django_db
def test_sem_senha_explica_o_que_falta(monkeypatch):
    monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "professor")
    monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
    with pytest.raises(CommandError):
        call_command("garantir_admin")


def test_leitor_de_env(tmp_path):
    arquivo = tmp_path / ".env"
    arquivo.write_text('# comentário\nA=1\nB = "com espaço"\n\nlinha sem igual\nC=x=y\n', encoding="utf-8")
    assert ler_env(arquivo) == {"A": "1", "B": "com espaço", "C": "x=y"}


def test_env_que_nao_existe_nao_quebra(tmp_path):
    assert ler_env(tmp_path / "nao_existe") == {}


@pytest.mark.django_db
def test_admin_pede_login(client):
    from django.urls import reverse
    resposta = client.get(reverse("admin:index"))   # o endereço vem do ADMIN_URL (web/.env)
    assert resposta.status_code == 302 and reverse("admin:login") in resposta["Location"]
