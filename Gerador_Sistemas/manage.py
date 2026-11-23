#!/usr/bin/env python
"""A tela do SGS pelo Django.

    cd Gerador_Sistemas        (ou da raiz do projeto: lá há um manage.py que repassa para este)
    python manage.py runserver              → http://127.0.0.1:6100 (o 00) e abre a janela de app (PWA)
    python manage.py runserver --sem-abrir  → só sobe o servidor
    python manage.py runserver 6150         → outra porta

É a mesma tela do `python Gerador_Sistemas/tela_prompt.py` (as rotas moram em tela_prompt.atender()).
"""
import os
import sys


def main():
    from sgs_web.ambiente import usar_o_venv_do_projeto

    usar_o_venv_do_projeto()          # .venv não ativado (ele fica na raiz)? roda de novo com o python dele
    os.environ["DJANGO_SETTINGS_MODULE"] = "sgs_web.settings"     # este manage.py é só do SGS
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
