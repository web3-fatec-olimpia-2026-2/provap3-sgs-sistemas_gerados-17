class PoliticaInteira:
    FATOR = 1.0

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaMeia:
    FATOR = 0.5

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaClube:
    FATOR = 0.8

    def aplicar(self, base):
        return round(base * self.FATOR, 2)


class PoliticaPromocional:
    FATOR = 0.6

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
