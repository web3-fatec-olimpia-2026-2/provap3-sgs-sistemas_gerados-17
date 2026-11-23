"""
Pharmas — VISITOR (GoF · comportamental): operações NOVAS sobre uma estrutura, sem mexer nela.

ANTES (nucleo/antes_orcamento.py): total_antigo e texto_antigo percorriam as linhas perguntando o
tipo — cada operação nova repetia a escada; cada tipo de linha novo mexia em todas.
DEPOIS (aqui):
  * cada tipo de linha tem aceitar(visitante) e chama o método CERTO do visitante (despacho duplo);
  * cada OPERAÇÃO é um visitante (CalculoDoTotal, TextoDoOrcamento) com um visitar_* por tipo;
  * operação nova = visitante novo (ContagemPorTipo) — as linhas não mudam.
Quando NÃO usar: se os TIPOS de elemento mudam muito (cada tipo novo obriga a mexer em todos os
visitantes) — aí prefira polimorfismo comum (um método em cada classe).
"""


class LinhaPharm:
    def __init__(self, item):
        self.item = item

    def aceitar(self, visitante):
        return visitante.visitar_pharm(self)


class LinhaExtra:
    def __init__(self, descricao, valor):
        self.descricao = descricao
        self.valor = valor

    def aceitar(self, visitante):
        return visitante.visitar_extra(self)


class LinhaDesconto:
    def __init__(self, valor):
        self.valor = valor  # valor positivo que será SUBTRAÍDO

    def aceitar(self, visitante):
        return visitante.visitar_desconto(self)


class Orcamento:
    """ESTRUTURA: guarda as linhas e deixa um visitante passar por todas."""

    def __init__(self, linhas):
        self.linhas = list(linhas)

    def aceitar(self, visitante):
        for linha in self.linhas:
            linha.aceitar(visitante)
        return visitante.resultado()


class CalculoDoTotal:
    """Visitante 1: soma o orçamento."""

    def __init__(self):
        self.total = 0.0

    def visitar_pharm(self, linha):
        self.total += linha.item.total

    def visitar_extra(self, linha):
        self.total += linha.valor

    def visitar_desconto(self, linha):
        self.total -= linha.valor

    def resultado(self):
        return round(self.total, 2)


class TextoDoOrcamento:
    """Visitante 2: descreve cada linha."""

    def __init__(self):
        self.linhas = []

    def visitar_pharm(self, linha):
        self.linhas.append(f"{linha.item.cliente}: R$ {linha.item.total:.2f}")

    def visitar_extra(self, linha):
        self.linhas.append(f"+ {linha.descricao}: R$ {linha.valor:.2f}")

    def visitar_desconto(self, linha):
        self.linhas.append(f"- desconto: R$ {linha.valor:.2f}")

    def resultado(self):
        return "\n".join(self.linhas)


class ContagemPorTipo:
    """Visitante NOVO: entrou sem mudar nenhuma linha."""

    def __init__(self):
        self.contagem = {"pharm": 0, "extra": 0, "desconto": 0}

    def visitar_pharm(self, linha):
        self.contagem["pharm"] += 1

    def visitar_extra(self, linha):
        self.contagem["extra"] += 1

    def visitar_desconto(self, linha):
        self.contagem["desconto"] += 1

    def resultado(self):
        return dict(self.contagem)
