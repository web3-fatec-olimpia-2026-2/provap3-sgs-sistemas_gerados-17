#!/usr/bin/env bash
unset DJANGO_SETTINGS_MODULE
# =============================================================================
# iniciar.sh — prepara e sobe o site Django do sistema "ViagemCerta" (gerado).
#
#   bash iniciar.sh                 tudo: venv → deps → .env → migrations → admin → servidor
#   bash iniciar.sh tudo 8001       tudo, em outra porta
#   bash iniciar.sh preparar        tudo, MENOS subir o servidor
#   bash iniciar.sh venv            cria .venv nesta pasta (se não existir)
#   bash iniciar.sh deps            instala o requirements.txt (só se faltar alguma dependência)
#   bash iniciar.sh env             cria web/.env a partir de web/.env.example (nunca sobrescreve)
#   bash iniciar.sh migrar          makemigrations viagcerts destinos + migrate
#   bash iniciar.sh admin           cria/atualiza o superusuário (dados do web/.env)
#   bash iniciar.sh testar          testes do núcleo e da web
#   bash iniciar.sh rodar [porta]   sobe o servidor em http://127.0.0.1:porta (Ctrl+C para parar)
#
# O site abre sozinho no navegador: PWA=1 (padrão, no web/.env) = janela de app isolada das abas;
# PWA=0 = aba comum; ABRIR=0 = não abre nada.
#
# Variáveis opcionais:
#   VENV=/caminho/.venv   usa um ambiente virtual que já existe (ex.: o da raiz do projeto)
#   PY=/caminho/python    usa um Python específico (ignora VENV)
#   PWA=0|1, ABRIR=0      como (e se) abrir o navegador
#   DJANGO_SUPERUSER_USERNAME / _EMAIL / _PASSWORD   têm prioridade sobre o web/.env
# =============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB="$RAIZ/web"
VENV="${VENV:-$RAIZ/.venv}"
PY="${PY:-$VENV/bin/python}"

passo() { printf '\n==> %s\n' "$*"; }

criar_venv() {
  if [ -x "$PY" ]; then echo "ambiente ok: $PY"; return; fi
  passo "criando o ambiente virtual em $VENV"
  python3 -m venv "$VENV"
}

instalar_deps() {
  if "$PY" -c "import django, pytest, pytest_django" 2>/dev/null; then
    echo "dependências ok (Django, pytest e pytest-django já instalados)"
    return
  fi
  passo "instalando as dependências do requirements.txt"
  "$PY" -m pip install -r "$RAIZ/requirements.txt"
}

criar_env() {
  if [ -f "$WEB/.env" ]; then echo "web/.env ok (já existe — não sobrescrevo)"; return; fi
  passo "criando web/.env a partir de web/.env.example"
  cp "$WEB/.env.example" "$WEB/.env"
  local py="$PY" chave
  [ -x "$py" ] || py=python3
  chave="$("$py" -c 'import secrets; print(secrets.token_urlsafe(40))')"
  sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$chave|" "$WEB/.env"   # chave secreta nova, só desta máquina
}

migrar() {
  passo "migrations"
  (cd "$WEB" && "$PY" manage.py makemigrations viagcerts destinos && "$PY" manage.py migrate)
}

criar_admin() {
  passo "superusuário"
  (cd "$WEB" && "$PY" manage.py garantir_admin)
}

testar() {
  passo "testes do núcleo"
  (cd "$RAIZ" && "$PY" -m pytest -q -p no:cacheprovider)
  passo "testes da web"
  (cd "$WEB" && "$PY" -m pytest -q -p no:cacheprovider)
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

rodar() {
  local porta="${1:-}"
  if [ -z "$porta" ] && [ -f "$WEB/.env" ]; then porta="$(sed -n 's/^PORTA=//p' "$WEB/.env" | tail -1)"; fi
  porta="${porta:-8000}"
  local admin=""
  [ -f "$WEB/.env" ] && admin="$(sed -n 's/^ADMIN_URL=//p' "$WEB/.env" | tail -1)"
  passo "site em http://127.0.0.1:$porta/  ·  admin em http://127.0.0.1:$porta/${admin:-admin/}  ·  Ctrl+C para parar"
  (sleep 2; abrir_navegador "http://127.0.0.1:$porta/") &   # abre depois que o servidor sobe
  cd "$WEB"
  # shellcheck disable=SC2086  # RUNSERVER_OPCOES pode ter várias opções (ex.: --noreload)
  exec "$PY" manage.py runserver "127.0.0.1:$porta" ${RUNSERVER_OPCOES:-}
}

case "${1:-tudo}" in
  tudo)      criar_venv; instalar_deps; criar_env; migrar; criar_admin; rodar "${2:-}" ;;
  preparar)  criar_venv; instalar_deps; criar_env; migrar; criar_admin ;;
  venv)      criar_venv ;;
  deps)      criar_venv; instalar_deps ;;
  env)       criar_env ;;
  migrar)    migrar ;;
  admin)     criar_admin ;;
  testar)    testar ;;
  rodar)     rodar "${2:-}" ;;
  ajuda|-h|--help) awk 'NR > 1 && /^set -euo/ { exit } NR > 1 && !/^# =/ { sub(/^# ?/, ""); print }' "$0" ;;
  *) echo "comando desconhecido: $1  (veja: bash iniciar.sh ajuda)" >&2; exit 2 ;;
esac
