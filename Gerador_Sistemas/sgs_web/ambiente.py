"""O .venv do projeto para os manage.py do SGS (o da raiz e o de Gerador_Sistemas/).

O .venv mora em Gerador_Sistemas/.venv (criado pelo Gerador_Sistemas/requirements.txt); na raiz do projeto há um
atalho .venv para ele, então `source .venv/bin/activate` vale nas duas pastas. Num terminal novo, sem ativar, o
python é o do sistema (`python3`, sem Django) e o runserver falharia — então o manage.py roda o MESMO comando de
novo com o python do .venv. Este módulo não importa o Django (é chamado antes, justamente para saber se ele existe).
"""
import os
import subprocess
import sys
from pathlib import Path

PASTA_SGS = Path(__file__).resolve().parents[1]              # sgs_web → Gerador_Sistemas
RAIZ_PROJETO = PASTA_SGS.parent
VENV_PYTHON = PASTA_SGS / ".venv" / "bin" / "python"
MARCA = "SGS_REEXEC"                                         # já trocou de python uma vez: não tenta de novo


def _achar_python_do_venv():
    """Procura o Python do .venv em Gerador_Sistemas/.venv ou na raiz (Linux/WSL e Windows)."""
    candidatos = (
        PASTA_SGS / ".venv" / "bin" / "python",
        PASTA_SGS / ".venv" / "Scripts" / "python.exe",
        RAIZ_PROJETO / ".venv" / "bin" / "python",
        RAIZ_PROJETO / ".venv" / "Scripts" / "python.exe",
    )
    for caminho in candidatos:
        if caminho.exists():
            return caminho
    return None


def usar_o_venv_do_projeto():
    """Com Django neste python: segue. Sem ele: roda de novo com o .venv do projeto (ou explica como criar/ativar)."""
    try:
        import django  # noqa: F401
    except ModuleNotFoundError:
        pass
    else:
        os.environ.pop(MARCA, None)
        return
    venv_python = _achar_python_do_venv()
    if venv_python is None or os.environ.get(MARCA) == "1":
        sys.exit(
            f"Django não encontrado neste python ({sys.executable}). Prepare e suba o ambiente com um comando:\n"
            f'    Linux/WSL: bash "{RAIZ_PROJETO / "iniciar.sh"}"   (ou: source iniciar.sh ativar)\n'
            f'    Windows:   "{RAIZ_PROJETO / "iniciar.bat"}"\n'
            f"Ou manualmente:\n"
            f'    cd "{PASTA_SGS}" && python3 -m venv .venv && source .venv/bin/activate '
            f"&& pip install -r requirements.txt"
        )
    print(f"(o .venv não está ativado — usando o do projeto: {venv_python})", file=sys.stderr, flush=True)
    os.environ[MARCA] = "1"
    if os.name == "nt":
        sys.exit(subprocess.call([str(venv_python), *sys.argv]))
    os.execv(str(venv_python), [str(venv_python), *sys.argv])
