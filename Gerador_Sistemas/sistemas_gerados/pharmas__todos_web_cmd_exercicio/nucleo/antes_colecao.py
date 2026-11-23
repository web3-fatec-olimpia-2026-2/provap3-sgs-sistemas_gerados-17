"""ANTES — o smell do Iterator: quem usa conhece a LISTA interna e percorre por índice."""


class ColecaoAntiga:
    def __init__(self):
        self._itens = []

    def adicionar(self, item):
        self._itens.append(item)


def totais_antigo(colecao):
    totais = []
    i = 0
    while i < len(colecao._itens):  # depende do detalhe interno (_itens é uma lista)
        totais.append(colecao._itens[i].total)
        i += 1
    return totais
