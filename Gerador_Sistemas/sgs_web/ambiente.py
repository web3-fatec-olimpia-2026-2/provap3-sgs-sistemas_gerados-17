"""O .venv do projeto para os manage.py do SGS (o da raiz e o de Gerador_Sistemas/).

O .venv mora em Gerador_Sistemas/.venv (criado pelo Gerador_Sistemas/requirements.txt); na raiz do projeto há um
atalho .venv para ele, então `source .venv/bin/activate` vale nas duas pastas. Num terminal novo, sem ativar, o
python é o do sistema (`python3`, sem Django) e o runserver falharia — então o manage.py roda o MESMO comando de
novo com o python do .venv. Este módulo não importa o Django (é chamado antes, justamente para saber se ele existe).
"""
import os
import sys
from pathlib import Path

PASTA_SGS = Path(__file__).resolve().parents[1]              # sgs_web → Gerador_Sistemas
VENV_PYTHON = PASTA_SGS / ".venv" / "bin" / "python"
MARCA = "SGS_REEXEC"                                         # já trocou de python uma vez: não tenta de novo


def usar_o_venv_do_projeto():
    """Com Django neste python: segue. Sem ele: roda de novo com o .venv do projeto (ou explica como criar/ativar)."""
    try:
        import django  # noqa: F401
    except ModuleNotFoundError:
        pass
    else:
        os.environ.pop(MARCA, None)
        return
    if not VENV_PYTHON.exists() or os.environ.get(MARCA) == "1":
        sys.exit(f"Django não encontrado neste python ({sys.executable}). Crie/ative o ambiente do projeto:\n"
                 f'    cd "{PASTA_SGS}" && python3 -m venv .venv && source .venv/bin/activate '
                 f"&& pip install -r requirements.txt")
    print(f"(o .venv não está ativado — usando o do projeto: {VENV_PYTHON})", file=sys.stderr, flush=True)
    os.environ[MARCA] = "1"
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])
