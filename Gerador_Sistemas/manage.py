#!/usr/bin/env python
"""A tela do SGS pelo Django.

    cd Gerador_Sistemas
    python manage.py runserver              → http://127.0.0.1:6100 (o 00) e abre a janela de app (PWA)
    python manage.py runserver --sem-abrir  → só sobe o servidor
    python manage.py runserver 6150         → outra porta

É a mesma tela do `python Gerador_Sistemas/tela_prompt.py` (as rotas moram em tela_prompt.atender()).
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sgs_web.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
