#!/usr/bin/env bash
unset DJANGO_SETTINGS_MODULE
# =============================================================================
# iniciar.sh — prepara e sobe o site Django do sistema "Pharmas" (gerado).
#
#   bash iniciar.sh                 tudo: venv → deps → .env → migrations → admin → servidor
#   bash iniciar.sh tudo 8001       tudo, em outra porta
#   bash iniciar.sh preparar        tudo, MENOS subir o servidor
#   source iniciar.sh ativar        prepara se precisar e ATIVA o .venv no seu terminal atual
#   bash iniciar.sh venv            cria .venv nesta pasta (se não existir)
#   bash iniciar.sh deps            instala o requirements.txt (só se faltar alguma dependência)
#   bash iniciar.sh env             cria web/.env a partir de web/.env.example (nunca sobrescreve)
#   bash iniciar.sh migrar          makemigrations pharns + migrate
#   bash iniciar.sh admin           cria/atualiza o superusuário (dados do web/.env)
#   bash iniciar.sh testar          testes do núcleo e da web
#   bash iniciar.sh rodar [porta]   sobe o servidor em http://127.0.0.1:porta (Ctrl+C para parar)
#
# O site abre sozinho no navegador: PWA=1 (padrão, no web/.env) = janela de app isolada das abas;
# PWA=0 = aba comum; ABRIR=0 = não abre nada.
#
# Variáveis opcionais:
#   VENV=/caminho/.venv   usa um ambiente virtual que já existe (ex.: o do SGS, Gerador_Sistemas/.venv)
#   PY=/caminho/python    usa um Python específico (ignora VENV)
#   PWA=0|1, ABRIR=0      como (e se) abrir o navegador
#   DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD   têm prioridade sobre o web/.env
# =============================================================================

_foi_sourced() { [ "${BASH_SOURCE[0]}" != "$0" ]; }

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB="$RAIZ/web"
_VENV_EXPLICITO="${VENV:-}"
_PY_EXPLICITO="${PY:-}"

_python_do_venv() {
  local v="$1"
  if [ -x "$v/bin/python" ]; then echo "$v/bin/python"; return 0; fi
  if [ -x "$v/Scripts/python.exe" ]; then echo "$v/Scripts/python.exe"; return 0; fi
  echo "$v/bin/python"
}

_activate_do_venv() {
  local v="$1"
  if [ -f "$v/bin/activate" ]; then echo "$v/bin/activate"; return 0; fi
  if [ -f "$v/Scripts/activate" ]; then echo "$v/Scripts/activate"; return 0; fi
  return 1
}

_resolver_venv() {
  if [ -n "$_VENV_EXPLICITO" ]; then
    VENV="$_VENV_EXPLICITO"
  elif [ -x "$RAIZ/.venv/bin/python" ] || [ -x "$RAIZ/.venv/Scripts/python.exe" ]; then
    VENV="$RAIZ/.venv"
  elif [ "${1:-}" != "venv" ] && { [ -x "$RAIZ/../../.venv/bin/python" ] || [ -x "$RAIZ/../../.venv/Scripts/python.exe" ]; }; then
    VENV="$(cd "$RAIZ/../.." && pwd)/.venv"
  else
    VENV="$RAIZ/.venv"
  fi
  if [ -n "$_PY_EXPLICITO" ]; then
    PY="$_PY_EXPLICITO"
  else
    PY="$(_python_do_venv "$VENV")"
  fi
}

passo() { printf '\n==> %s\n' "$*"; }

achar_python_base() {
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

criar_venv() {
  if [ -x "$PY" ]; then echo "ambiente ok: $PY"; return 0; fi
  # O Python exigido está no cabeçalho do requirements.txt (o pip não instala Python).
  local py_base
  if ! py_base="$(achar_python_base)"; then
    echo "ERRO: este sistema precisa do Python 3.12 ou mais novo — achei $(python3 --version 2>&1 || python --version 2>&1 || echo 'nenhum Python')" >&2
    return 1
  fi
  passo "criando o ambiente virtual em $VENV (com $py_base)"
  if ! "$py_base" -m venv "$VENV"; then
    rm -rf "$VENV"
    echo "ERRO: falhou ao criar o ambiente virtual em $VENV." >&2
    echo "      No Ubuntu/WSL, instale o pacote venv:  sudo apt update && sudo apt install -y python3-venv" >&2
    return 1
  fi
  PY="$(_python_do_venv "$VENV")"
}

instalar_deps() {
  [ -f "$RAIZ/requirements.txt" ] || return 0
  # Tudo do requirements.txt já instalado? (--no-index: o pip só confere o que já está aqui, sem internet)
  if "$PY" -m pip install -q --disable-pip-version-check --no-index -r "$RAIZ/requirements.txt" \
       >/dev/null 2>&1; then
    echo "dependências ok (todas as do requirements.txt já estão instaladas)"
    return 0
  fi
  passo "instalando as dependências do requirements.txt"
  "$PY" -m pip install --upgrade pip >/dev/null 2>&1 || true
  "$PY" -m pip install -r "$RAIZ/requirements.txt"
}

criar_env() {
  [ -f "$WEB/.env.example" ] || { echo "web/.env.example não encontrado — pulando .env"; return 0; }
  if [ -f "$WEB/.env" ]; then echo "web/.env ok (já existe — não sobrescrevo)"; return 0; fi
  passo "criando web/.env a partir de web/.env.example"
  cp "$WEB/.env.example" "$WEB/.env"
  local py="$PY"
  [ -x "$py" ] || py="$(achar_python_base || echo python3)"
  "$py" -c 'import pathlib, re, secrets, sys; p = pathlib.Path(sys.argv[1]); p.write_text(re.sub(r"^SECRET_KEY=.*$", "SECRET_KEY=" + secrets.token_urlsafe(40), p.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8", newline="\n")' "$WEB/.env"
}

migrar() {
  [ -f "$WEB/manage.py" ] || return 0
  passo "migrations"
  (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" manage.py makemigrations pharns && "$PY" manage.py migrate)
}

criar_admin() {
  [ -f "$WEB/manage.py" ] || return 0
  passo "superusuário"
  (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" manage.py garantir_admin)
}

testar() {
  passo "testes do núcleo"
  (unset DJANGO_SETTINGS_MODULE; cd "$RAIZ" && "$PY" -m pytest -q -p no:cacheprovider)
  passo "testes da web"
  (unset DJANGO_SETTINGS_MODULE; cd "$WEB" && "$PY" -m pytest -q -p no:cacheprovider)
}

abrir_navegador() {
  # PWA=1: janela de app (--app = sem abas nem barra de endereço) · PWA=0: aba comum do navegador padrão.
  local url="$1" exe="" pwa="${PWA:-}"
  [ "${ABRIR:-1}" = "0" ] && return 0
  [ -z "$pwa" ] && [ -f "$WEB/.env" ] && pwa="$(sed -n 's/^PWA=//p' "$WEB/.env" | tail -1)"
  for candidato in "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
                   "/mnt/c/Program Files/Microsoft/Edge/Application/msedge.exe" \
                   "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"; do
    if [ -x "$candidato" ]; then exe="$candidato"; break; fi
  done
  if [ "${pwa:-1}" = "1" ] && [ -n "$exe" ]; then ("$exe" --app="$url" >/dev/null 2>&1 &)
  elif command -v wslview >/dev/null 2>&1; then (wslview "$url" >/dev/null 2>&1 &)
  elif [ -x /mnt/c/Windows/System32/cmd.exe ]; then (cd /mnt/c && /mnt/c/Windows/System32/cmd.exe /c start "" "$url" >/dev/null 2>&1 &)
  elif command -v xdg-open >/dev/null 2>&1; then (xdg-open "$url" >/dev/null 2>&1 &)
  fi
  return 0
}

porta_livre() {
  "$PY" -c "import socket, sys; s = socket.socket(); rc = s.connect_ex(('127.0.0.1', int(sys.argv[1]))); s.close(); sys.exit(0 if rc != 0 else 1)" "$1"
}

rodar() {
  local porta="${1:-}"
  if [ -z "$porta" ] && [ -f "$WEB/.env" ]; then porta="$(sed -n 's/^PORTA=//p' "$WEB/.env" | tail -1)"; fi
  porta="${porta:-8000}"
  if ! porta_livre "$porta"; then
    echo "ERRO: a porta $porta já está em uso. Tente outra porta:  bash iniciar.sh rodar $((porta + 1))" >&2
    return 1
  fi
  local admin=""
  [ -f "$WEB/.env" ] && admin="$(sed -n 's/^ADMIN_URL=//p' "$WEB/.env" | tail -1)"
  passo "site em http://127.0.0.1:$porta/  ·  admin em http://127.0.0.1:$porta/${admin:-admin/}  ·  Ctrl+C para parar"
  (sleep 2; abrir_navegador "http://127.0.0.1:$porta/") &   # abre depois que o servidor sobe
  unset DJANGO_SETTINGS_MODULE
  cd "$WEB"
  # shellcheck disable=SC2086  # RUNSERVER_OPCOES pode ter várias opções (ex.: --noreload)
  exec "$PY" manage.py runserver "127.0.0.1:$porta" ${RUNSERVER_OPCOES:-}
}

_resolver_venv "${1:-tudo}"

if _foi_sourced; then
  criar_venv || return 1
  instalar_deps || return 1
  criar_env || return 1
  _ACT="$(_activate_do_venv "$VENV")" || { echo "ERRO: activate não encontrado em $VENV" >&2; return 1; }
  # shellcheck disable=SC1090
  source "$_ACT"
  echo "ambiente ativado: $VENV"
  return 0
fi

set -euo pipefail
case "${1:-tudo}" in
  tudo)      criar_venv; instalar_deps; criar_env; migrar; criar_admin; rodar "${2:-}" ;;
  preparar)  criar_venv; instalar_deps; criar_env; migrar; criar_admin ;;
  ativar)    criar_venv; instalar_deps; echo "Para ativar no terminal atual, rode:  source iniciar.sh ativar" ;;
  venv)      criar_venv ;;
  deps)      criar_venv; instalar_deps ;;
  env)       criar_env ;;
  migrar)    migrar ;;
  admin)     criar_admin ;;
  testar)    testar ;;
  rodar)     rodar "${2:-}" ;;
  ajuda|-h|--help) awk 'NR > 1 && /^_foi_sourced/ { exit } NR > 1 && !/^# =/ { sub(/^# ?/, ""); print }' "$0" ;;
  *) echo "comando desconhecido: $1  (veja: bash iniciar.sh ajuda)" >&2; exit 2 ;;
esac
