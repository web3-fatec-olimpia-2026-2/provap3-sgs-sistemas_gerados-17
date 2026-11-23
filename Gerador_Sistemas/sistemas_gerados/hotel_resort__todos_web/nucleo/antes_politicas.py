"""ANTES — o smell do Strategy: um if/elif por tipo de hóspede que cresce a cada regra nova."""


class CobrancaAntiga:
    def __init__(self, item, tipo):
        self.item = item
        self.tipo = tipo  # um TEXTO decide o comportamento

    def valor(self):
        base = self.item.total
        if self.tipo == "comum":
            return round(base * 1.0, 2)
        elif self.tipo == "fidelidade":
            return round(base * 0.9, 2)
        elif self.tipo == "parceiro":
            return round(base * 0.8, 2)
        else:
            raise ValueError(f"tipo de hóspede desconhecido: {self.tipo}")
