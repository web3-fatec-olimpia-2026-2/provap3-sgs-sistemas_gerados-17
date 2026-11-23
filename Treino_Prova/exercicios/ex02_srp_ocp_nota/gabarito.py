"""ex02 — GABARITO comentado: SRP (uma classe, um motivo para mudar) + OCP (formato novo por extensão)."""


class PedidoFazTudo:
    """Mantido para os testes compararem: tinha 3 motivos para mudar (regra, layout, destino)."""

    def __init__(self, cliente, itens):
        self.cliente = cliente
        self.itens = itens

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


# --- 1 motivo para mudar: a REGRA do total ---
class Pedido:
    def __init__(self, cliente, itens):
        self.cliente = cliente
        self.itens = list(itens)        # cópia: o pedido não depende da lista de quem o criou

    def total(self):
        return sum(preco * qtd for _, preco, qtd in self.itens)


# --- 1 motivo para mudar: o LAYOUT da nota em texto ---
class NotaTextoFormatter:
    def formatar(self, pedido):
        # Só LÊ o pedido (recebido por parâmetro). Texto idêntico ao antigo → refatoração segura.
        linhas = [f"NOTA - {pedido.cliente}"]
        for nome, preco, qtd in pedido.itens:
            linhas.append(f"{qtd}x {nome} = R$ {preco * qtd:.2f}")
        linhas.append(f"TOTAL: R$ {pedido.total():.2f}")
        return "\n".join(linhas)


# --- formato NOVO = classe NOVA (OCP): Pedido e NotaTextoFormatter não foram tocados ---
class NotaCsvFormatter:
    SEP = ";"

    def formatar(self, pedido):
        linhas = [self.SEP.join(["item", "qtd", "subtotal"])]
        for nome, preco, qtd in pedido.itens:
            linhas.append(self.SEP.join([nome, str(qtd), f"{preco * qtd:.2f}"]))
        linhas.append(self.SEP.join(["TOTAL", "", f"{pedido.total():.2f}"]))
        return "\n".join(linhas)


# --- 1 motivo para mudar: o DESTINO (arquivo hoje; banco/S3 amanhã) ---
class ArquivoRepository:
    def salvar(self, texto, caminho):
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)


# Para explicar na P3:
# - PedidoFazTudo mudava se a regra, o layout OU o destino mudassem (3 motivos) → viola SRP.
# - PDF amanhã = NotaPdfFormatter com formatar(pedido); não toco em Pedido, nos outros formatters
#   nem no repository (OCP).
# - Não criei "CalculaSubtotal", "SomaTotal"... — isso seria separar por MÉTODO, não por
#   responsabilidade; o total é uma responsabilidade só.
