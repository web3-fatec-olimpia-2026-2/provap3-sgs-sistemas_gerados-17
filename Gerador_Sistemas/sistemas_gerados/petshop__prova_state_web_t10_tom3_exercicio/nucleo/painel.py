"""
PETShop — MVVM (Aulas 08/09): o ViewModel prepara a vitrine; a View só serve.

MODEL     = os dicts crus em ITENS (codigo, categoria, preco, disponivel)
VIEWMODEL = ItemViewModel / PainelVM → dado PRONTO para a tela, sem saber desenhar
VIEW      = tela_painel_mvvm → só costura o que o ViewModel preparou (zero if)
No Django não há data binding: o ViewModel é só a preparação chamada antes do render.
Service × ViewModel: regra de negócio (o que é verdade) × lógica de exibição (como aparece).
"""

ITENS = [
    {'codigo': 1, 'categoria': 'basico', 'preco': 100.0, 'disponivel': True},
    {'codigo': 2, 'categoria': 'intermediario', 'preco': 200.0, 'disponivel': False},
    {'codigo': 3, 'categoria': 'premium', 'preco': 400.0, 'disponivel': True}
]


class ItemViewModel:
    """Prepara UM item para exibição. Não sabe o que é tela: entrega texto pronto."""

    def __init__(self, item):
        self.codigo = item["codigo"]
        self.categoria = item["categoria"]
        self.disponivel = bool(item["disponivel"])  # estado derivado, num lugar só
        self.status_label = "disponível" if self.disponivel else "INDISPONÍVEL"
        self.acao_label = "Solicitar" if self.disponivel else "(indisponível)"
        self.preco_formatado = f"R$ {item['preco']:.2f}"


class PainelVM:
    """Prepara o PAINEL: um ViewModel por item, a contagem e o rodapé."""

    def __init__(self, itens):
        self.itens = [ItemViewModel(i) for i in itens]
        self.livres = sum(1 for i in self.itens if i.disponivel)
        self.rodape = f"{self.livres} recurso(s) disponível(is)" if self.livres else "SEM DISPONIBILIDADE"


def tela_painel_mvvm(itens):
    """View 'burra': só lê o ViewModel."""
    painel = PainelVM(itens)
    linhas = [f"Recurso {i.codigo} [{i.categoria}] - {i.preco_formatado} - {i.status_label} - {i.acao_label}"
              for i in painel.itens]
    return "\n".join(linhas) + "\n" + painel.rodape
