"""
ViagemCerta — ABSTRACT FACTORY (GoF · criação): FAMÍLIAS de peças que combinam entre si.

ANTES (nucleo/antes_kits.py): cada peça do relatório (cabeçalho, linha, rodapé) tinha o seu
"if formato"; bastava esquecer um para misturar texto com HTML no mesmo relatório.
DEPOIS (aqui):
  * KitRelatorio (a FÁBRICA ABSTRATA) declara criar_cabecalho / criar_linha / criar_rodape;
  * cada kit concreto (KitTexto, KitHtml) cria TODAS as peças da MESMA família;
  * montar_relatorio(kit, itens) só conhece a interface → família nova = kit novo (KitMarkdown).
Quando NÃO usar: só uma família (ou uma peça) — Factory Method ou a classe direta bastam.
"""


class KitRelatorio:
    """FÁBRICA ABSTRATA: o que toda família de peças precisa saber criar."""

    def criar_cabecalho(self, titulo):
        raise NotImplementedError

    def criar_linha(self, rotulo, valor):
        raise NotImplementedError

    def criar_rodape(self, total):
        raise NotImplementedError


class KitTexto(KitRelatorio):
    """Família TEXTO: todas as peças em texto puro."""

    def criar_cabecalho(self, titulo):
        return f"== {titulo} =="

    def criar_linha(self, rotulo, valor):
        return f"{rotulo}: R$ {valor:.2f}"

    def criar_rodape(self, total):
        return f"TOTAL: R$ {total:.2f}"


class KitHtml(KitRelatorio):
    """Família HTML: todas as peças em HTML (nunca se misturam com texto)."""

    def criar_cabecalho(self, titulo):
        return f"<h1>{titulo}</h1>"

    def criar_linha(self, rotulo, valor):
        return f"<li>{rotulo}: R$ {valor:.2f}</li>"

    def criar_rodape(self, total):
        return f"<p><strong>TOTAL: R$ {total:.2f}</strong></p>"


class KitMarkdown(KitRelatorio):
    """Família NOVA (extensão): entra sem mudar montar_relatorio."""

    def criar_cabecalho(self, titulo):
        return f"# {titulo}"

    def criar_linha(self, rotulo, valor):
        return f"- {rotulo}: R$ {valor:.2f}"

    def criar_rodape(self, total):
        return f"**TOTAL: R$ {total:.2f}**"


def montar_relatorio(kit, itens):
    """CLIENTE: usa só a interface do kit → todas as peças vêm da MESMA família."""
    partes = [kit.criar_cabecalho("ViagemCerta")]
    partes += [kit.criar_linha(item.cliente, item.total) for item in itens]
    partes.append(kit.criar_rodape(round(sum(item.total for item in itens), 2)))
    return "\n".join(partes)
