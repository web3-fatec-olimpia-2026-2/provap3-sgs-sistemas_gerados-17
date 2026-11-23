"""Cópia estática do Django Study Hub num ÚNICO .html (abre com duplo clique, sem servidor e sem rede).

Uso: python3 -I montar_study_hub.py <pasta_baixada> <pasta_saida>
  <pasta_baixada>: index.html, src/style.css, src/app.js, data/*.json e README.md, como vieram do site
  <pasta_saida>:   recebe django_study_hub.html e django_study_hub_arquivos/ (os originais, sem mudança)

O layout é o do site: o index.html, o style.css e o app.js entram IGUAIS (só embutidos).
Únicas mudanças: (1) os 14 JSON vão embutidos e um fetch() mínimo os entrega ao app.js — abrindo por
file:// o navegador bloquearia o fetch('./data/...'); (2) a origem e a data entram como comentário,
<meta> e uma linha no rodapé do próprio site.
"""
import json
import re
import shutil
import sys
from pathlib import Path

ORIGEM = "https://mrsautchuk.github.io/django-study-hub/"
REPO = "https://github.com/MrSautchuk/django-study-hub"
COMMIT = "d5008d7a2bfee40bb094906b090f6e5a26713c86"
DATA_COMMIT = "21/11/2026"
INCORPORADO = "23/11/2026"
NOME = "django_study_hub"

base, saida = Path(sys.argv[1]), Path(sys.argv[2])
index = (base / "index.html").read_text(encoding="utf-8")
css = (base / "src" / "style.css").read_text(encoding="utf-8")
js = (base / "src" / "app.js").read_text(encoding="utf-8")
lista = re.search(r"Promise\.all\(\[([^\]]+)\]", js).group(1)
nomes = re.findall(r"'([\w-]+)'", lista)
assert len(nomes) == 14, nomes
assert "</script" not in js.lower() and "<!--" not in js and "</style" not in css.lower()


def json_seguro(nome):
    """JSON validado e seguro dentro de <script type=application/json> (sem '</' nem '<!--')."""
    texto = (base / "data" / f"{nome}.json").read_text(encoding="utf-8")
    json.loads(texto)
    return texto.replace("</", "<\\/").replace("<!--", "<\\u0021--")


dados = "\n".join(f'<script type="application/json" id="dsh-dados-{n}">{json_seguro(n)}</script>' for n in nomes)
ponte = """<script>
/* Cópia estática: entrega ao app.js os JSON embutidos acima no lugar de fetch('./data/<nome>.json'). */
(function () {
  var original = window.fetch;
  window.fetch = function (url) {
    var m = /^\\.\\/data\\/([\\w-]+)\\.json$/.exec(String(url));
    var el = m && document.getElementById('dsh-dados-' + m[1]);
    if (el) return Promise.resolve(new Response(el.textContent, {headers: {'Content-Type': 'application/json'}}));
    return original ? original.apply(this, arguments) : Promise.reject(new Error('sem fetch'));
  };
})();
</script>"""

cabecalho = f"""<!--
  Cópia estática para referência de estudo — Django Study Hub
  Fonte: {ORIGEM}
  Repositório: {REPO} (commit {COMMIT[:7]}, de {DATA_COMMIT})
  Incorporada ao projeto em: {INCORPORADO}
  Layout original: index.html, src/style.css e src/app.js embutidos sem alteração; os 14 arquivos data/*.json
  vão embutidos e são entregues ao app.js pelo fetch() da "ponte" (file:// bloquearia a leitura).
  Originais como vieram do site: {NOME}_arquivos/
-->
"""
metas = (f'<meta name="sgs-origem" content="{ORIGEM}">\n  '
         f'<meta name="sgs-incorporado-em" content="{INCORPORADO}">')
nota_rodape = (f'<span>CÓPIA ESTÁTICA DE <a href="{ORIGEM}" target="_blank" rel="noopener">MRSAUTCHUK.GITHUB.IO/DJANGO-STUDY-HUB</a>'
               f' <b>·</b> INCORPORADA EM {INCORPORADO}</span>')

html = index
html = html.replace("<!doctype html>", "<!doctype html>\n" + cabecalho, 1)
html = html.replace('<link rel="stylesheet" href="./src/style.css">', f"{metas}\n  <style>\n{css}\n  </style>", 1)
html = html.replace('<script defer src="./src/app.js"></script>', "", 1)
html = html.replace("<span>Consulta local, sem IA", nota_rodape + "<span>Consulta local, sem IA", 1)
html = html.replace("</body>", f"{dados}\n{ponte}\n<script>\n{js}\n</script>\n</body>", 1)
for trecho in ("./src/style.css", "./src/app.js"):
    assert trecho not in html, trecho
assert nota_rodape in html and "sgs-origem" in html

saida.mkdir(parents=True, exist_ok=True)
(saida / f"{NOME}.html").write_text(html, encoding="utf-8", newline="\n")
originais = saida / f"{NOME}_arquivos"
if originais.exists():
    shutil.rmtree(originais)
originais.mkdir()
shutil.copy2(base / "index.html", originais / "index.html")
shutil.copy2(base / "README.md", originais / "README.md")
shutil.copytree(base / "src", originais / "src")
shutil.copytree(base / "data", originais / "data")
print("ok:", len(html), "bytes ·", len(nomes), "JSON embutidos")
