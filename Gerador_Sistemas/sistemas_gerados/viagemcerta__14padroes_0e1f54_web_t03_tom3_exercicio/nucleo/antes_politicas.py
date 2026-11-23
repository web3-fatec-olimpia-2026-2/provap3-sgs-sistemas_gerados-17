"""ANTES — o smell do Strategy: um if/elif por tipo de cliente que cresce a cada regra nova."""


class CobrancaAntiga:
    def __init__(self, item, tipo):
        self.item = item
        self.tipo = tipo  # um TEXTO decide o comportamento

    def valor(self):
        base = self.item.total
        if self.tipo == "comum":
            return round(base * 1.0, 2)
        elif self.tipo == "fidelidade":
            return round(base * 0.92, 2)
        elif self.tipo == "corporativo":
            return round(base * 0.85, 2)
        else:
            raise ValueError(f"tipo de cliente desconhecido: {self.tipo}")
