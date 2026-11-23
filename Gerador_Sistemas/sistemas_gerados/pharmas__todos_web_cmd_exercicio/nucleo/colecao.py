"""
Pharmas — ITERATOR (GoF · comportamental): percorrer a coleção sem conhecer o que tem dentro.

ANTES (nucleo/antes_colecao.py): quem usava lia colecao._itens[i] com índice — dependia da lista
interna; trocar a lista por dicionário quebraria todos os laços.
DEPOIS (aqui):
  * ColecaoPharm guarda as Pharms do jeito que quiser (aqui: dicionário por cliente);
  * __iter__ devolve um ITERADOR (IteradorDeItens, com __next__) → funciona com for, list() e sum();
  * percursos especiais (acima_de, ordenados_por_total) não expõem o interior.
Quando NÃO usar: lista e dicionário já são iteráveis em Python; a classe de iterador só vale para
percurso especial (filtrado, em ordem própria). Um gerador (yield) é o atalho pythônico.
"""


class IteradorDeItens:
    """ITERADOR: guarda a POSIÇÃO do percurso (cada for ganha o seu)."""

    def __init__(self, itens):
        self._itens = itens
        self._posicao = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._posicao >= len(self._itens):
            raise StopIteration  # avisa o for que acabou
        item = self._itens[self._posicao]
        self._posicao += 1
        return item


class ColecaoPharm:
    """AGREGADO: guarda as Pharms por cliente (a estrutura interna é segredo dela)."""

    def __init__(self):
        self._por_chave = {}

    def adicionar(self, item):
        self._por_chave[item.cliente] = item

    def __len__(self):
        return len(self._por_chave)

    def __iter__(self):
        """Percurso padrão: na ordem em que foram adicionadas."""
        return IteradorDeItens(list(self._por_chave.values()))

    def acima_de(self, valor):
        """Percurso FILTRADO: só os de total acima do valor (gerador = iterador pronto do Python)."""
        for item in self._por_chave.values():
            if item.total > valor:
                yield item

    def ordenados_por_total(self):
        """Percurso em OUTRA ORDEM, sem mudar a coleção."""
        return IteradorDeItens(sorted(self._por_chave.values(), key=lambda item: item.total))
