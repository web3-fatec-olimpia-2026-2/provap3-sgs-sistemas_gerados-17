"""ex02 — SRP + OCP. SEU ARQUIVO (não mexa em PedidoFazTudo; resolva os TODOs)."""


class PedidoFazTudo:
    """O SMELL: dados + regra + apresentação + infraestrutura juntos."""

    def __init__(self, cliente, itens):
        self.cliente = cliente
        self.itens = itens                      # [(nome, preco_unitario, quantidade), ...]

    def total(self):
        return sum(preco * qtd for _, preco, qtd in self.itens)

    def gerar_nota(self):
        linhas = [f"NOTA - {self.cliente}"]
        for nome, preco, qtd in self.itens:
            linhas.append(f"{qtd}x {nome} = R$ {preco * qtd:.2f}")
        linhas.append(f"TOTAL: R$ {self.total():.2f}")
        return "\n".join(linhas)

    def salvar(self, caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(self.gerar_nota())


class Pedido:
    def __init__(self, cliente, itens):
        raise NotImplementedError   # TODO

    def total(self):
        raise NotImplementedError   # TODO


class NotaTextoFormatter:
    def formatar(self, pedido):
        raise NotImplementedError   # TODO: texto idêntico ao gerar_nota()


class NotaCsvFormatter:
    def formatar(self, pedido):
        raise NotImplementedError   # TODO


class ArquivoRepository:
    def salvar(self, texto, caminho):
        raise NotImplementedError   # TODO
