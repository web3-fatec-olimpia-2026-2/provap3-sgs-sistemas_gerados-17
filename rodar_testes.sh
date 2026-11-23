#!/bin/bash
# Roda os testes de TODAS as resoluções e sistemas gerados, uma pasta por vez.
# (Cada pasta é independente: vários labs têm um "quarto.py"/"test_quarto.py" com o mesmo
#  nome, então rodar tudo de uma vez a partir da raiz confundiria os imports.)
#
# Uso (no WSL, na raiz do projeto):  bash rodar_testes.sh
#      só uma parte:                 bash rodar_testes.sh Aula05
#                                    bash rodar_testes.sh Gerador_Sistemas

cd "$(dirname "$0")" || exit 1
RAIZ="$(pwd)"
PY="$RAIZ/Gerador_Sistemas/.venv/bin/python"     # o .venv do projeto (na raiz, .venv é um atalho para ele)
[ -x "$PY" ] || PY="$RAIZ/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

filtro="${1:-}"
falhas=0
total=0

# Para cada test_*.py, a "pasta de teste" é a mais próxima (subindo) que tem pytest.ini.
# Sem pytest.ini acima: a pasta do arquivo (ou a mãe, se o arquivo estiver em tests/).
pasta_de_teste() {
  local d="$1" fallback="$1"
  [ "$(basename "$fallback")" = "tests" ] && fallback=$(dirname "$fallback")
  while [ "$d" != "." ] && [ "$d" != "/" ]; do
    if [ -f "$d/pytest.ini" ]; then echo "$d"; return; fi
    d=$(dirname "$d")
  done
  echo "$fallback"
}

mapfile -t pastas < <(
  find . -name .venv -prune -o -path ./Extras -prune -o -path '*/material_original' -prune \
       -o -path '*/gabarito' -prune -o -name 'test_*.py' -print |
  while read -r f; do pasta_de_teste "$(dirname "$f")"; done | sort -u
)

for d in "${pastas[@]}"; do
  [[ -n "$filtro" && "$d" != *"$filtro"* ]] && continue
  total=$((total + 1))
  rotulo="$d"
  ambiente=()
  # Sistemas gerados em modo exercício: testa a resolução do gabarito (a do aluno começa com TODO).
  if [ -d "$d/gabarito" ]; then ambiente=(env ALVO=gabarito); rotulo="$d (gabarito)"; fi
  printf '%-90s ' "$rotulo"
  saida=$(cd "$d" && "${ambiente[@]}" "$PY" -m pytest -q -p no:cacheprovider 2>&1)
  if [ $? -eq 0 ]; then
    echo "OK  ($(echo "$saida" | tail -1))"
  else
    falhas=$((falhas + 1))
    echo "FALHOU"
    echo "$saida" | tail -25
  fi
done

echo
echo "Pastas testadas: $total · com falha: $falhas"
exit $falhas
