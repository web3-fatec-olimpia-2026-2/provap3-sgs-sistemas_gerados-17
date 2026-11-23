"""Cópia estática da página da Wikipédia COM o layout original (CSS do Vector 2022 copiado localmente).

Uso: python3 -I montar_wikipedia.py <pasta_baixada> <pasta_saida>
  <pasta_baixada>: pagina.html + estilo1.css..estilo3.css (baixados da Wikipédia)
  <pasta_saida>:   recebe wikipedia_padrao_de_projeto_de_software.html e a pasta _arquivos/
"""
import re
import sys
import urllib.request
from pathlib import Path

ORIGEM = "https://pt.wikipedia.org"
NOME = "wikipedia_padrao_de_projeto_de_software"
UA = {"User-Agent": "Mozilla/5.0 (estudo; copia-estatica)"}

base, saida = Path(sys.argv[1]), Path(sys.argv[2])
pasta = saida / f"{NOME}_arquivos"
pasta.mkdir(parents=True, exist_ok=True)


def baixar(url, nome):
    """Baixa uma imagem/ícone para a pasta de arquivos (uma vez) e devolve o caminho relativo."""
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = ORIGEM + url
    destino = pasta / nome
    if not destino.exists():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            destino.write_bytes(r.read())
    return f"{NOME}_arquivos/{nome}"


def nome_de(url):
    nome = url.split("?")[0].rstrip("/").split("/")[-1]
    return re.sub(r"[^A-Za-z0-9._]", "_", nome)


html = (base / "pagina.html").read_text(encoding="utf-8")
revid = re.search(r'"wgRevisionId":(\d+)', html).group(1)

# 1) sem JavaScript: a página fica no modo "client-nojs" do próprio Vector (menus funcionam só com CSS)
html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S)
html = re.sub(r"<noscript>.*?</noscript>", "", html, flags=re.S)   # só havia o pixel de login central
html = re.sub(r'<img src="https://pt\.wikipedia\.org/wiki/Special:CentralAutoLogin[^>]*>', "", html)

# 2) <link>: fica só o CSS (local), o canonical e a licença; o resto dependia do servidor
folhas = []


def trocar_link(m):
    tag = m.group(0)
    if 'rel="stylesheet"' in tag:
        folhas.append(tag)
        return f'<link rel="stylesheet" href="{NOME}_arquivos/estilo{len(folhas)}.css">'
    if 'rel="canonical"' in tag or 'rel="license"' in tag:
        return tag
    if 'rel="icon"' in tag:
        return f'<link rel="icon" href="{baixar("/static/favicon/wikipedia.ico", "wikipedia.ico")}">'
    if 'rel="mw:PageProp/Category"' in tag:
        return tag.replace('href="./', f'href="{ORIGEM}/wiki/')
    return ""


html = re.sub(r"<link\b[^>]*>", trocar_link, html)

# 3) CSS local: url(/w/...) → arquivo baixado; url(//...) → https (só usados em outras páginas)
for i in range(1, len(folhas) + 1):
    css = (base / f"estilo{i}.css").read_text(encoding="utf-8")

    def url_local(m):
        alvo = m.group(1).strip("'\"")
        return f"url({baixar(alvo, nome_de(alvo))[len(NOME) + 10:]})"

    css = re.sub(r"url\((['\"]?/[^/][^)]*)\)", url_local, css)
    css = re.sub(r"url\((['\"]?)//", r"url(\1https://", css)
    (pasta / f"estilo{i}.css").write_text(css, encoding="utf-8")

# 4) imagens da página → cópia local (sem srcset: uma resolução basta para estudo)
html = re.sub(r'\s(srcset)="[^"]*"', "", html)


def img_local(m):
    alvo = m.group(1).replace("&amp;", "&")
    return f'src="{baixar(alvo, nome_de(alvo))}"'


html = re.sub(r'src="((?://|/)[^"]+)"', img_local, html)

# 5) links: tudo o que era relativo ao servidor passa a apontar para a Wikipédia (online)
html = html.replace('href="./', f'href="{ORIGEM}/wiki/')
html = re.sub(r'(href|action)="/(?!/)', rf'\1="{ORIGEM}/', html)
html = re.sub(r'(href|resource)="//', r'\1="https://', html)

# 6) moldura de referência (a única coisa acrescentada ao conteúdo)
moldura = f"""
<style>
  .sgs-referencia {{ font: 13px/1.5 sans-serif; background: #eaf3ff; color: #202122; border-bottom: 1px solid #a2a9b1;
                     padding: 8px 16px; }}
  .sgs-referencia p {{ margin: 2px auto; max-width: 1200px; }}
  .sgs-referencia a {{ color: #3366cc; }}
</style>
<div class="sgs-referencia" role="note">
  <p><strong>Cópia estática para referência de estudo</strong> — artigo da Wikipédia em português, com o layout original
     (HTML e CSS da Wikipédia copiados para <code>{NOME}_arquivos/</code>; scripts removidos).</p>
  <p><strong>Fonte:</strong> <a href="{ORIGEM}/wiki/Padr%C3%A3o_de_projeto_de_software">{ORIGEM}/wiki/Padr%C3%A3o_de_projeto_de_software</a>
     · <strong>Revisão:</strong> <a href="{ORIGEM}/w/index.php?title=Padr%C3%A3o_de_projeto_de_software&amp;oldid={revid}">oldid={revid}</a>
     · <strong>Incorporada em:</strong> 22/11/2026 · <strong>Layout atualizado em:</strong> 23/11/2026 (mesma revisão).</p>
  <p><strong>Licença:</strong> <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.pt-br">CC BY-SA 4.0</a> ·
     autores: <a href="{ORIGEM}/w/index.php?title=Padr%C3%A3o_de_projeto_de_software&amp;action=history">histórico de edições</a>.
     Usada pelo gerador como referência da lista GoF (23 padrões). Os links abrem o site da Wikipédia.</p>
</div>
"""
html = re.sub(r"(<body\b[^>]*>)", lambda m: m.group(1) + moldura, html, count=1)
html = html.replace("<title>", "<title>[Cópia de referência] ", 1)

assert "<script" not in html
(saida / f"{NOME}.html").write_text(html, encoding="utf-8", newline="\n")
print("revisão", revid, "· folhas", len(folhas), "· arquivos", sorted(p.name for p in pasta.iterdir()))
