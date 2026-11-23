"""
VIEWMODEL (Aula 08): prepara o que a tela mostra. Recebe dados do Service; não sabe desenhar.
No servidor não há binding (isso é do Alpine.js no navegador): aqui é só preparação antes do render.
"""


class ItemVM:
    def __init__(self, obj, valor_final):
        self.id = obj.pk
        self.titulo = f"{obj.leitor} — {obj.dias} dia(s)"
        self.tipo_label = obj.get_tipo_display()
        self.valor_formatado = f"R$ {valor_final:.2f}"
        self.tem_desconto = valor_final < float(obj.total)
        self.selo = "com desconto" if self.tem_desconto else "valor cheio"


class PainelVM:
    def __init__(self, objetos, servico):
        itens, total = servico.resumo(objetos)
        self.itens = [ItemVM(obj, valor) for obj, valor in itens]
        self.total_formatado = f"R$ {total:.2f}"
        if self.itens:
            self.rodape = f"{len(self.itens)} registro(s) · total {self.total_formatado}"
        else:
            self.rodape = "Nenhum registro ainda"
