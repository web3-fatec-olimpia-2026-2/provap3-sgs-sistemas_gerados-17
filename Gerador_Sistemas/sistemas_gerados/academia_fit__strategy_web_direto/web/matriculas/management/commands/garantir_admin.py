"""
`python manage.py garantir_admin`: cria (ou atualiza) o superusuário a partir do ambiente / web/.env.

Usa as mesmas variáveis do `createsuperuser --noinput` do Django:
DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL e DJANGO_SUPERUSER_PASSWORD.
Diferença: pode rodar quantas vezes quiser — se o usuário já existe, atualiza e-mail e senha.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria ou atualiza o superusuário com os dados do web/.env (pode rodar várias vezes)."

    def handle(self, *args, **opcoes):
        usuario = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        senha = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        if not usuario or not senha:
            raise CommandError("defina DJANGO_SUPERUSER_USERNAME e DJANGO_SUPERUSER_PASSWORD no web/.env")
        modelo = get_user_model()
        obj, criado = modelo.objects.get_or_create(username=usuario, defaults={"email": email})
        obj.email = email
        obj.is_staff = obj.is_superuser = True
        obj.set_password(senha)  # guarda o HASH da senha, nunca o texto
        obj.save()
        self.stdout.write(self.style.SUCCESS(f"superusuário {'criado' if criado else 'atualizado'}: {usuario}"))
