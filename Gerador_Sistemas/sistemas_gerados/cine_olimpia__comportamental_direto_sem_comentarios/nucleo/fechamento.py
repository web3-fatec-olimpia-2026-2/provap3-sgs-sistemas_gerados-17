class Fechamento:
    def fechar(self, item):
        self.validar(item)
        valor = self.calcular(item)
        valor = self.ajustar(valor)
        return self.formatar(valor)

    def validar(self, item):
        if item.total < 0:
            raise ValueError("total negativo")

    def calcular(self, item):
        return item.total

    def ajustar(self, valor):
        return valor

    def formatar(self, valor):
        return f"R$ {valor:.2f}"


class FechamentoPadrao(Fechamento):
    pass


class FechamentoComTaxa(Fechamento):
    TAXA = 0.1

    def ajustar(self, valor):
        return round(valor * (1 + self.TAXA), 2)


class FechamentoMeia(Fechamento):
    def ajustar(self, valor):
        return round(valor * 0.5, 2)
