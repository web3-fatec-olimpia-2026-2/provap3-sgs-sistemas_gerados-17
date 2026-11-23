class IteradorDeItens:
    def __init__(self, itens):
        self._itens = itens
        self._posicao = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._posicao >= len(self._itens):
            raise StopIteration
        item = self._itens[self._posicao]
        self._posicao += 1
        return item


class ColecaoIngresso:
    def __init__(self):
        self._por_chave = {}

    def adicionar(self, item):
        self._por_chave[item.espectador] = item

    def __len__(self):
        return len(self._por_chave)

    def __iter__(self):
        return IteradorDeItens(list(self._por_chave.values()))

    def acima_de(self, valor):
        for item in self._por_chave.values():
            if item.total > valor:
                yield item

    def ordenados_por_total(self):
        return IteradorDeItens(sorted(self._por_chave.values(), key=lambda item: item.total))
