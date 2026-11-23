"""
Hotel Resort — BRIDGE (GoF · estrutural): duas dimensões que variam SEPARADAS.

ANTES (nucleo/antes_comprovantes.py): uma classe para cada COMBINAÇÃO (Simples×Texto, Simples×Html,
Detalhado×Texto, Detalhado×Html) — 2 tipos × 2 formatos = 4 classes com código repetido; um formato
novo exigiria uma classe para CADA tipo.
DEPOIS (aqui):
  * ABSTRAÇÃO: Comprovante (Simples, Detalhado) decide O QUE mostrar;
  * IMPLEMENTAÇÃO: Formato (FormatoTexto, FormatoHtml) decide COMO escrever;
  * a "ponte" é o atributo self.formato: o comprovante TEM-UM formato (composição) e delega;
  * formato novo (FormatoMarkdown) vale para TODOS os tipos: N + M classes em vez de N × M.
Quando NÃO usar: só uma dimensão varia → herança simples ou Strategy resolvem.
"""


class Formato:
    """IMPLEMENTAÇÃO: como escrever um título e uma linha."""

    def titulo(self, texto):
        raise NotImplementedError

    def linha(self, rotulo, valor):
        raise NotImplementedError


class FormatoTexto(Formato):
    def titulo(self, texto):
        return texto.upper()

    def linha(self, rotulo, valor):
        return f"{rotulo}: {valor}"


class FormatoHtml(Formato):
    def titulo(self, texto):
        return f"<h2>{texto}</h2>"

    def linha(self, rotulo, valor):
        return f"<p>{rotulo}: {valor}</p>"


class FormatoMarkdown(Formato):
    """Formato NOVO: vale para todos os comprovantes sem criar combinações."""

    def titulo(self, texto):
        return f"## {texto}"

    def linha(self, rotulo, valor):
        return f"- **{rotulo}**: {valor}"


class Comprovante:
    """ABSTRAÇÃO: TEM-UM formato (a ponte) e decide o conteúdo."""

    def __init__(self, formato):
        self.formato = formato

    def gerar(self, item):
        raise NotImplementedError


class ComprovanteSimples(Comprovante):
    def gerar(self, item):
        return "\n".join([self.formato.titulo("Comprovante"),
                          self.formato.linha("Total", f"R$ {item.total:.2f}")])


class ComprovanteDetalhado(Comprovante):
    def gerar(self, item):
        return "\n".join([self.formato.titulo("Comprovante detalhado"),
                          self.formato.linha("Hospede", item.hospede),
                          self.formato.linha("Diarias", item.diarias),
                          self.formato.linha("Valor diaria", f"R$ {item.valor_diaria:.2f}"),
                          self.formato.linha("Total", f"R$ {item.total:.2f}")])
