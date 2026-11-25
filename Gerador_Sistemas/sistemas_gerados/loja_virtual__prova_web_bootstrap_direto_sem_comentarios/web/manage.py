import os
import sys


def main():
    # Se herdado do SGS (manage.py da tela), limpa antes do setdefault para usar o settings deste sistema.
    if os.environ.get("DJANGO_SETTINGS_MODULE") == "sgs_web.settings":
        os.environ.pop("DJANGO_SETTINGS_MODULE", None)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
