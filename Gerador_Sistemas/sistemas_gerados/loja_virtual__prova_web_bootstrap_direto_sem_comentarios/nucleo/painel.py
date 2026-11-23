ITENS = [
    {'codigo': 501, 'categoria': 'produto', 'preco': 50.0, 'disponivel': True},
    {'codigo': 502, 'categoria': 'eletronico', 'preco': 300.0, 'disponivel': False},
    {'codigo': 503, 'categoria': 'livro', 'preco': 40.0, 'disponivel': True}
]


class ItemViewModel:
    def __init__(self, item):
        self.codigo = item["codigo"]
        self.categoria = item["categoria"]
        self.disponivel = bool(item["disponivel"])
        self.status_label = "em estoque" if self.disponivel else "ESGOTADO"
        self.acao_label = "Comprar" if self.disponivel else "(avise-me)"
        self.preco_formatado = f"R$ {item['preco']:.2f}"


class PainelVM:
    def __init__(self, itens):
        self.itens = [ItemViewModel(i) for i in itens]
        self.livres = sum(1 for i in self.itens if i.disponivel)
        self.rodape = f"{self.livres} produto(s) em estoque" if self.livres else "SEM ESTOQUE - nenhum produto disponível"


def tela_painel_mvvm(itens):
    painel = PainelVM(itens)
    linhas = [f"Produto {i.codigo} [{i.categoria}] - {i.preco_formatado} - {i.status_label} - {i.acao_label}"
              for i in painel.itens]
    return "\n".join(linhas) + "\n" + painel.rodape
