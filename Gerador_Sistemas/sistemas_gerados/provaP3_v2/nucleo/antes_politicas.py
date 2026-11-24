"""ANTES — o smell do Strategy: um if/elif por destino da fruta que cresce a cada regra nova."""


class CobrancaAntiga:
    def __init__(self, item, tipo):
        self.item = item
        self.tipo = tipo  # um TEXTO decide o comportamento

    def valor(self):
        base = self.item.total
        if self.tipo == "industria":
            return round(base * 1.0, 2)
        elif self.tipo == "mesa":
            return round(base * 1.25, 2)
        elif self.tipo == "exportacao":
            return round(base * 1.4, 2)
        else:
            raise ValueError(f"destino da fruta desconhecido: {self.tipo}")
