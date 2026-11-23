"""
Hotel Resort — COMPOSITE (GoF · estrutural): item e PACOTE de itens tratados do mesmo jeito.

ANTES (nucleo/antes_pacotes.py): total_antigo(coisa) pergunta com isinstance se é lista ou Reserva
e se chama de novo para as listas — cada operação nova repete essa checagem.
DEPOIS (aqui):
  * Componente define a interface comum: preco() e descricao();
  * Unitario (FOLHA) embrulha uma Reserva;
  * Pacote (COMPOSTO) guarda filhos (folhas OU outros pacotes) e repassa a pergunta a eles;
  * quem usa chama pacote.preco() sem saber a profundidade da árvore.
Quando NÃO usar: lista plana, sem pacotes dentro de pacotes → sum() numa lista basta.
"""


class Componente:
    """Interface comum de folha e composto."""

    def preco(self):
        raise NotImplementedError

    def descricao(self, nivel=0):
        raise NotImplementedError


class Unitario(Componente):
    """FOLHA: uma Reserva sozinha."""

    def __init__(self, item):
        self.item = item

    def preco(self):
        return self.item.total

    def descricao(self, nivel=0):
        return "  " * nivel + f"{self.item.hospede}: R$ {self.preco():.2f}"


class Pacote(Componente):
    """COMPOSTO: tem filhos (folhas ou pacotes) e trata todos pela mesma interface."""

    def __init__(self, nome, desconto=0.0):
        self.nome = nome
        self.desconto = desconto  # ex.: 0.1 = pacote com 10% de desconto
        self.filhos = []

    def adicionar(self, componente):
        self.filhos.append(componente)
        return self  # permite encadear

    def preco(self):
        soma = sum(filho.preco() for filho in self.filhos)  # recursão: cada filho sabe o seu preço
        return round(soma * (1 - self.desconto), 2)

    def descricao(self, nivel=0):
        linhas = ["  " * nivel + f"[{self.nome}] R$ {self.preco():.2f}"]
        linhas += [filho.descricao(nivel + 1) for filho in self.filhos]
        return "\n".join(linhas)
