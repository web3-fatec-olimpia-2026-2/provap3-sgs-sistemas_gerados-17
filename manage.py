#!/usr/bin/env python
"""Atalho da RAIZ do projeto para a tela do SGS pelo Django.

    python manage.py runserver              → http://127.0.0.1:6100 (o 00) e abre a janela de app (PWA)
    python manage.py runserver --sem-abrir  → só sobe o servidor
    python manage.py runserver 6150         → outra porta

É a mesma tela do `python Gerador_Sistemas/tela_prompt.py`. O projeto Django dela mora em Gerador_Sistemas/
(manage.py e sgs_web/); este arquivo só põe aquela pasta no caminho e chama o Django.
"""
import os
import sys
from pathlib import Path

PASTA_SGS = Path(__file__).resolve().parent / "Gerador_Sistemas"


def main():
    sys.path.insert(0, str(PASTA_SGS))
    from sgs_web.ambiente import usar_o_venv_do_projeto

    usar_o_venv_do_projeto()          # .venv não ativado? roda de novo com o python dele
    os.environ["DJANGO_SETTINGS_MODULE"] = "sgs_web.settings"     # este manage.py é só do SGS
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
