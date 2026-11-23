"""ANTES — o smell do Bridge: uma classe por COMBINAÇÃO (tipos × formatos), com código repetido."""


class SimplesTexto:
    def gerar(self, item):
        return "\n".join(["COMPROVANTE", f"Total: R$ {item.total:.2f}"])


class SimplesHtml:
    def gerar(self, item):
        return "\n".join(["<h2>Comprovante</h2>", f"<p>Total: R$ {item.total:.2f}</p>"])


class DetalhadoTexto:
    def gerar(self, item):
        return "\n".join(["COMPROVANTE DETALHADO", f"Hospede: {item.hospede}", f"Diarias: {item.diarias}",
                          f"Valor diaria: R$ {item.valor_diaria:.2f}", f"Total: R$ {item.total:.2f}"])


class DetalhadoHtml:
    def gerar(self, item):
        return "\n".join(["<h2>Comprovante detalhado</h2>", f"<p>Hospede: {item.hospede}</p>",
                          f"<p>Diarias: {item.diarias}</p>", f"<p>Valor diaria: R$ {item.valor_diaria:.2f}</p>",
                          f"<p>Total: R$ {item.total:.2f}</p>"])
