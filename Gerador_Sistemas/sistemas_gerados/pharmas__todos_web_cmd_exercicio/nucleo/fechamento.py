"""
Pharmas — TEMPLATE METHOD (GoF · comportamental): o ROTEIRO é fixo; só alguns passos mudam.

ANTES (nucleo/antes_fechamento.py): fechar_padrao_antigo e fechar_com_taxa_antigo eram cópias quase
iguais do mesmo roteiro (validar → calcular → ajustar → formatar) — corrigir um passo exigia lembrar
de corrigir em todas as cópias.
DEPOIS (aqui):
  * Fechamento.fechar(item) é o MÉTODO TEMPLATE: define a ORDEM dos passos e não é sobrescrito;
  * os passos que variam (ajustar) são sobrescritos pelas subclasses; o GANCHO tem padrão vazio;
  * fechamento novo = subclasse que muda só o passo dela.
Template Method × Strategy: aqui a variação vem por HERANÇA (subclasse); no Strategy, por
COMPOSIÇÃO (objeto injetado). Quando NÃO usar: só um passo varia → passe uma função (Strategy).
"""


class Fechamento:
    """CLASSE ABSTRATA com o método template fechar()."""

    def fechar(self, item):
        """MÉTODO TEMPLATE: a ordem dos passos é sempre a mesma."""
        self.validar(item)
        valor = self.calcular(item)
        valor = self.ajustar(valor)
        return self.formatar(valor)

    def validar(self, item):
        if item.total < 0:
            raise ValueError("total negativo")

    def calcular(self, item):
        return item.total

    def ajustar(self, valor):
        """GANCHO: por padrão não muda nada."""
        return valor

    def formatar(self, valor):
        return f"R$ {valor:.2f}"


class FechamentoPadrao(Fechamento):
    """Usa o roteiro sem mudar nenhum passo."""


class FechamentoComTaxa(Fechamento):
    TAXA = 0.1

    def ajustar(self, valor):
        return round(valor * (1 + self.TAXA), 2)


class FechamentoEspecial(Fechamento):
    """Fechamento NOVO (Especial): só o passo ajustar muda."""

    def ajustar(self, valor):
        return round(valor * 0.9, 2)
