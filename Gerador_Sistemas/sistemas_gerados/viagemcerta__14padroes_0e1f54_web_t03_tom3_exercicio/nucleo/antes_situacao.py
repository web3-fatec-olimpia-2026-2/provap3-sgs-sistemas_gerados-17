"""ANTES — o smell do State: a mesma escada de if/elif sobre o status em CADA método."""


class SituacaoAntiga:
    def __init__(self, item):
        self.item = item
        self.status = "aberto"

    def confirmar(self):
        if self.status == "aberto":
            self.status = "confirmado"
        else:
            raise ValueError(f"não dá para confirmar: está {self.status}")

    def concluir(self):
        if self.status == "confirmado":
            self.status = "concluido"
        else:
            raise ValueError(f"não dá para concluir: está {self.status}")

    def cancelar(self):
        if self.status in ("aberto", "confirmado"):
            self.status = "cancelado"
        else:
            raise ValueError(f"não dá para cancelar: está {self.status}")
