class PoliticaComum:
    FATOR = 1.0

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaFidelidade:
    FATOR = 0.9

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaAtacado:
    FATOR = 0.85

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaFuncionario:
    FATOR = 0.7

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class Cobranca:
    def __init__(self, item, politica):
        self.item = item
        self.politica = politica

    def valor(self):
        return self.politica.aplicar(self.item.total)


class CobrancaComFuncao:
    def __init__(self, item, politica):
        self.item = item
        self.politica = politica

    def valor(self):
        return self.politica(self.item.total)
