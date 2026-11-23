"""ANTES — o smell do Bridge: uma classe por COMBINAÇÃO (tipos × formatos), com código repetido."""


class SimplesTexto:
    def gerar(self, item):
        return "\n".join(["COMPROVANTE", f"Total: R$ {item.total:.2f}"])


class SimplesHtml:
    def gerar(self, item):
        return "\n".join(["<h2>Comprovante</h2>", f"<p>Total: R$ {item.total:.2f}</p>"])


class DetalhadoTexto:
    def gerar(self, item):
        return "\n".join(["COMPROVANTE DETALHADO", f"Cliente: {item.cliente}", f"Quantidade: {item.quantidade}",
                          f"Valor unitario: R$ {item.valor_unitario:.2f}", f"Total: R$ {item.total:.2f}"])


class DetalhadoHtml:
    def gerar(self, item):
        return "\n".join(["<h2>Comprovante detalhado</h2>", f"<p>Cliente: {item.cliente}</p>",
                          f"<p>Quantidade: {item.quantidade}</p>", f"<p>Valor unitario: R$ {item.valor_unitario:.2f}</p>",
                          f"<p>Total: R$ {item.total:.2f}</p>"])
