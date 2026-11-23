class LinhaIngresso:
    def __init__(self, item):
        self.item = item

    def aceitar(self, visitante):
        return visitante.visitar_ingresso(self)


class LinhaExtra:
    def __init__(self, descricao, valor):
        self.descricao = descricao
        self.valor = valor

    def aceitar(self, visitante):
        return visitante.visitar_extra(self)


class LinhaDesconto:
    def __init__(self, valor):
        self.valor = valor

    def aceitar(self, visitante):
        return visitante.visitar_desconto(self)


class Orcamento:
    def __init__(self, linhas):
        self.linhas = list(linhas)

    def aceitar(self, visitante):
        for linha in self.linhas:
            linha.aceitar(visitante)
        return visitante.resultado()


class CalculoDoTotal:
    def __init__(self):
        self.total = 0.0

    def visitar_ingresso(self, linha):
        self.total += linha.item.total

    def visitar_extra(self, linha):
        self.total += linha.valor

    def visitar_desconto(self, linha):
        self.total -= linha.valor

    def resultado(self):
        return round(self.total, 2)


class TextoDoOrcamento:
    def __init__(self):
        self.linhas = []

    def visitar_ingresso(self, linha):
        self.linhas.append(f"{linha.item.espectador}: R$ {linha.item.total:.2f}")

    def visitar_extra(self, linha):
        self.linhas.append(f"+ {linha.descricao}: R$ {linha.valor:.2f}")

    def visitar_desconto(self, linha):
        self.linhas.append(f"- desconto: R$ {linha.valor:.2f}")

    def resultado(self):
        return "\n".join(self.linhas)


class ContagemPorTipo:
    def __init__(self):
        self.contagem = {"ingresso": 0, "extra": 0, "desconto": 0}

    def visitar_ingresso(self, linha):
        self.contagem["ingresso"] += 1

    def visitar_extra(self, linha):
        self.contagem["extra"] += 1

    def visitar_desconto(self, linha):
        self.contagem["desconto"] += 1

    def resultado(self):
        return dict(self.contagem)
