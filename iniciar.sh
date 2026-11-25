#!/usr/bin/env bash
# =============================================================================
# iniciar.sh — prepara e sobe o ambiente do projeto (SGS e sistemas gerados).
#
#   bash iniciar.sh                     tudo: venv → deps → .env (se houver) → runserver do SGS (porta 6100)
#   bash iniciar.sh tudo [porta]        tudo, em outra porta (ex.: 6150)
#   bash iniciar.sh preparar            prepara .venv, atalho na raiz, deps e .env (sem subir servidor)
#   source iniciar.sh ativar            prepara se precisar e ATIVA o .venv no seu terminal atual
#   bash iniciar.sh venv                cria Gerador_Sistemas/.venv e o atalho .venv na raiz
#   bash iniciar.sh deps                instala Gerador_Sistemas/requirements.txt (só se faltar algo)
#   bash iniciar.sh env                 cria .env a partir de .env.example (se existir; nunca sobrescreve)
#   bash iniciar.sh migrar              roda makemigrations + migrate se houver banco/apps no projeto
#   bash iniciar.sh provap3 [porta]     prepara o ambiente e sobe o sistema provaP3 (migrations, admin, runserver)
#   bash iniciar.sh sistema <nome> [p]  prepara o ambiente e sobe qualquer sistema em sistemas_gerados/<nome>
#   bash iniciar.sh testar [filtro]     garante o ambiente e roda rodar_testes.sh
#   bash iniciar.sh rodar [porta]       sobe o servidor do SGS (porta 6100 por padrão)
#   bash iniciar.sh ajuda               mostra esta ajuda
#
# Variáveis opcionais:
#   VENV=/caminho/.venv   usa um ambiente virtual existente
#   PY=/caminho/python    usa um Python específico (ignora VENV)
#   ABRIR=0               passa --sem-abrir ao runserver do SGS
# =============================================================================

_sgs_foi_sourced() {
  [ "${BASH_SOURCE[0]}" != "$0" ]
}

_sgs_passo() { printf '\n==> %s\n' "$*"; }

_sgs_achar_python_base() {
  local cand
  for cand in python3 python3.14 python3.13 python3.12 python; do
    if command -v "$cand" >/dev/null 2>&1; then
      if "$cand" -c 'import sys; sys.exit(sys.version_info < (3, 12))' 2>/dev/null; then
        echo "$cand"
        return 0
      fi
    fi
  done
  return 1
}

_sgs_python_do_venv() {
  local v="$1"
  if [ -x "$v/bin/python" ]; then echo "$v/bin/python"; return 0; fi
  if [ -x "$v/Scripts/python.exe" ]; then echo "$v/Scripts/python.exe"; return 0; fi
  echo "$v/bin/python"
}

_sgs_activate_do_venv() {
  local v="$1"
  if [ -f "$v/bin/activate" ]; then echo "$v/bin/activate"; return 0; fi
  if [ -f "$v/Scripts/activate" ]; then echo "$v/Scripts/activate"; return 0; fi
  return 1
}

_sgs_criar_venv() {
  PY="$(_sgs_python_do_venv "$VENV")"
  if [ -n "${SGS_PY_EXPLICITO:-}" ] && [ -x "$SGS_PY_EXPLICITO" ]; then
    PY="$SGS_PY_EXPLICITO"
    echo "ambiente ok: $PY"
    return 0
  fi
  if [ -x "$PY" ] && "$PY" -m pip --version >/dev/null 2>&1; then
    echo "ambiente ok: $PY"
    return 0
  fi
  local py_base
  if ! py_base="$(_sgs_achar_python_base)"; then
    echo "ERRO: este projeto precisa do Python 3.12 ou mais novo (Django 6)." >&2
    echo "      Encontrado: $(python3 --version 2>&1 || python --version 2>&1 || echo 'nenhum Python no PATH')" >&2
    return 1
  fi
  _sgs_passo "criando o ambiente virtual em $VENV (com $py_base)"
  if ! "$py_base" -m venv "$VENV"; then
    rm -rf "$VENV"
    echo "ERRO: falhou ao criar o ambiente virtual em $VENV." >&2
    echo "      No Ubuntu/WSL, instale o pacote venv:  sudo apt update && sudo apt install -y python3-venv" >&2
    return 1
  fi
  PY="$(_sgs_python_do_venv "$VENV")"
}

_sgs_garantir_atalho_venv() {
  if [ "$VENV" = "$SGS_DIR/.venv" ] && [ ! -e "$RAIZ/.venv" ]; then
    ln -s "Gerador_Sistemas/.venv" "$RAIZ/.venv" 2>/dev/null || true
  fi
}

_sgs_instalar_deps() {
  if "$PY" -m pip install -q --disable-pip-version-check --no-index -r "$REQ_FILE" >/dev/null 2>&1; then
    echo "dependências ok (todas as do requirements.txt já estão instaladas)"
    return 0
  fi
  _sgs_passo "instalando as dependências de $REQ_FILE"
  "$PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
  "$PY" -m pip install -r "$REQ_FILE"
}

_sgs_criar_env_em() {
  local dir="$1"
  if [ ! -f "$dir/.env.example" ]; then
    return 0
  fi
  if [ -f "$dir/.env" ]; then
    echo "$dir/.env ok (já existe — não sobrescrevo)"
    return 0
  fi
  _sgs_passo "criando $dir/.env a partir de .env.example"
  cp "$dir/.env.example" "$dir/.env"
  local py_exec="$PY"
  [ -x "$py_exec" ] || py_exec="$(_sgs_achar_python_base || echo python3)"
  "$py_exec" - "$dir/.env" <<'PYEOF'
import pathlib, re, secrets, sys
arq = pathlib.Path(sys.argv[1])
texto = arq.read_text(encoding="utf-8")
chave = secrets.token_urlsafe(40)
novo = re.sub(r"^SECRET_KEY=.*$", f"SECRET_KEY={chave}", texto, flags=re.M)
arq.write_text(novo, encoding="utf-8", newline="\n")
PYEOF
}

_sgs_criar_env() {
  local achou=0
  for d in "$RAIZ" "$SGS_DIR"; do
    if [ -f "$d/.env.example" ]; then
      _sgs_criar_env_em "$d"
      achou=1
    fi
  done
  if [ "$achou" -eq 0 ]; then
    echo ".env: o SGS não precisa de .env próprio (os sistemas gerados criam o web/.env deles)"
  fi
}

_sgs_migrar() {
  # O SGS (sgs_web) não usa banco de dados (DATABASES = {}); só migra se algum dia passar a usar.
  local tem_db
  tem_db="$(unset DJANGO_SETTINGS_MODULE; cd "$SGS_DIR" && "$PY" -c '
import os, sys
sys.path.insert(0, ".")
os.environ["DJANGO_SETTINGS_MODULE"] = "sgs_web.settings"
from django.conf import settings
print("1" if settings.DATABASES else "0")
' 2>/dev/null || echo 0)"
  if [ "$tem_db" = "1" ]; then
    _sgs_passo "migrations do SGS"
    (unset DJANGO_SETTINGS_MODULE; cd "$SGS_DIR" && "$PY" manage.py migrate)
  else
    echo "migrations: o SGS não usa banco (cada sistema gerado aplica as próprias migrations ao subir)"
  fi
}

_sgs_porta_livre() {
  local porta="$1"
  "$PY" -c "import socket, sys; s = socket.socket(); rc = s.connect_ex(('127.0.0.1', int(sys.argv[1]))); s.close(); sys.exit(0 if rc != 0 else 1)" "$porta"
}

_sgs_rodar() {
  local porta="${1:-6100}"
  if ! _sgs_porta_livre "$porta"; then
    echo "ERRO: a porta $porta já está em uso. Já existe um SGS aberto?" >&2
    echo "      Para subir em outra porta:  bash iniciar.sh rodar $((porta + 50))" >&2
    return 1
  fi
  local opcoes=()
  [ "${ABRIR:-1}" = "0" ] && opcoes+=(--sem-abrir)
  _sgs_passo "subindo o SGS em http://127.0.0.1:$porta/  ·  Ctrl+C para parar"
  unset DJANGO_SETTINGS_MODULE
  cd "$RAIZ"
  exec "$PY" manage.py runserver "127.0.0.1:$porta" "${opcoes[@]}"
}

_sgs_rodar_sistema() {
  local nome="$1" porta="${2:-}"
  local pasta="$SGS_DIR/sistemas_gerados/$nome"
  if [ ! -d "$pasta" ]; then
    echo "ERRO: sistema não encontrado em $pasta" >&2
    echo "      Sistemas disponíveis:" >&2
    ls -1 "$SGS_DIR/sistemas_gerados" >&2
    return 1
  fi
  if [ ! -f "$pasta/iniciar.sh" ]; then
    echo "ERRO: $pasta não possui iniciar.sh" >&2
    return 1
  fi
  _sgs_passo "preparando e subindo o sistema $nome (usando $VENV)"
  unset DJANGO_SETTINGS_MODULE
  if [ -n "$porta" ]; then
    VENV="$VENV" PY="$PY" bash "$pasta/iniciar.sh" tudo "$porta"
  else
    VENV="$VENV" PY="$PY" bash "$pasta/iniciar.sh" tudo
  fi
}

_sgs_ajuda() {
  awk 'NR > 1 && /^_sgs_foi_sourced/ { exit } NR > 1 && !/^# =/ { sub(/^# ?/, ""); print }' "$SCRIPT_PATH"
}

_sgs_main() {
  SCRIPT_PATH="${BASH_SOURCE[0]}"
  RAIZ="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
  SGS_DIR="$RAIZ/Gerador_Sistemas"
  REQ_FILE="$SGS_DIR/requirements.txt"
  SGS_PY_EXPLICITO="${PY:-}"
  VENV="${VENV:-$SGS_DIR/.venv}"
  PY="$(_sgs_python_do_venv "$VENV")"

  unset DJANGO_SETTINGS_MODULE

  if _sgs_foi_sourced; then
    local acao="${1:-ativar}"
    if [ "$acao" = "ajuda" ] || [ "$acao" = "-h" ] || [ "$acao" = "--help" ]; then
      _sgs_ajuda
      return 0
    fi
    _sgs_criar_venv || return 1
    _sgs_garantir_atalho_venv
    _sgs_instalar_deps || return 1
    _sgs_criar_env
    local act
    if act="$(_sgs_activate_do_venv "$VENV")"; then
      # shellcheck disable=SC1090
      source "$act"
      echo "ambiente ativado: $VENV  (python: $(command -v python))"
      return 0
    fi
    echo "ERRO: não encontrei o script activate em $VENV" >&2
    return 1
  fi

  set -euo pipefail
  case "${1:-tudo}" in
    tudo)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      _sgs_criar_env
      _sgs_migrar
      _sgs_rodar "${2:-6100}"
      ;;
    preparar)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      _sgs_criar_env
      _sgs_migrar
      printf '\nAmbiente pronto! Para ativar no terminal atual:\n  source iniciar.sh ativar\nPara subir o SGS:\n  bash iniciar.sh\nPara subir a Prova P3:\n  bash iniciar.sh provap3\n'
      ;;
    ativar)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      echo ""
      echo "Para deixar o .venv ativado NO SEU TERMINAL ATUAL, rode com source:"
      echo "    source iniciar.sh ativar"
      ;;
    venv)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      ;;
    deps)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      ;;
    env)
      _sgs_criar_env
      ;;
    migrar)
      _sgs_criar_venv
      _sgs_migrar
      ;;
    provap3)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      _sgs_rodar_sistema "provaP3" "${2:-}"
      ;;
    sistema)
      if [ -z "${2:-}" ]; then
        echo "Uso: bash iniciar.sh sistema <nome_da_pasta> [porta]" >&2
        exit 2
      fi
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      _sgs_rodar_sistema "$2" "${3:-}"
      ;;
    testar)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      bash "$RAIZ/rodar_testes.sh" "${2:-}"
      ;;
    rodar)
      _sgs_criar_venv
      _sgs_garantir_atalho_venv
      _sgs_instalar_deps
      _sgs_rodar "${2:-6100}"
      ;;
    ajuda|-h|--help)
      _sgs_ajuda
      ;;
    *)
      echo "comando desconhecido: $1  (veja: bash iniciar.sh ajuda)" >&2
      exit 2
      ;;
  esac
}

_sgs_main "$@"
