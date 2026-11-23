"""ex03 — GABARITO comentado: Service (regra de negócio) × ViewModel (lógica de exibição)."""
from datetime import date

PEDIDOS = [
    {"id": 1, "cliente": "Ana",   "valor_itens": 100.0, "cupom": True,  "prazo": date(2026, 11, 20), "entregue": True},
    {"id": 2, "cliente": "Bruno", "valor_itens": 80.0,  "cupom": True,  "prazo": date(2026, 11, 18), "entregue": False},
    {"id": 3, "cliente": "Caio",  "valor_itens": 250.0, "cupom": False, "prazo": date(2026, 11, 30), "entregue": False},
]


def tela_pedidos(pedidos, hoje):
    """ANTES (mantido para comparação)."""
    linhas = []
    atrasados = 0
    for p in pedidos:
        total = p["valor_itens"]
        if p["cupom"] and total >= 100:
            total = total * 0.9
        if p["entregue"]:
            status, cor = "ENTREGUE", "verde"
        elif hoje > p["prazo"]:
            status, cor = "ATRASADO", "vermelho"
            atrasados += 1
        else:
            status, cor = "A CAMINHO", "amarelo"
        linhas.append(f"#{p['id']} {p['cliente']} - R$ {total:.2f} - {status} ({cor})")
    rodape = f"{atrasados} pedido(s) atrasado(s)" if atrasados else "Tudo em dia"
    return "\n".join(linhas) + "\n" + rodape


# ---------------------------------------------------------------------------
# SERVICE — o que é VERDADE no negócio (vale para tela, API, relatório...). Sem texto, sem cor.
# ---------------------------------------------------------------------------
class PedidoService:
    DESCONTO_CUPOM = 0.10
    MINIMO_CUPOM = 100

    def total(self, pedido):
        valor = pedido["valor_itens"]
        if pedido["cupom"] and valor >= self.MINIMO_CUPOM:
            return valor * (1 - self.DESCONTO_CUPOM)
        return valor

    def esta_atrasado(self, pedido, hoje):
        # Atraso é fato do domínio (gera multa, e-mail ao cliente...), não detalhe de tela.
        return (not pedido["entregue"]) and hoje > pedido["prazo"]


# ---------------------------------------------------------------------------
# VIEWMODEL — COMO mostrar. Pergunta ao Service e traduz em rótulo/cor/formato.
# ---------------------------------------------------------------------------
class PedidoViewModel:
    def __init__(self, pedido, hoje, servico=None):
        servico = servico or PedidoService()     # injeção opcional: facilita testar com um fake
        self.id = pedido["id"]
        self.cliente = pedido["cliente"]
        self.total_formatado = f"R$ {servico.total(pedido):.2f}"
        self.atrasado = servico.esta_atrasado(pedido, hoje)
        if pedido["entregue"]:
            self.status_label, self.cor = "ENTREGUE", "verde"
        elif self.atrasado:
            self.status_label, self.cor = "ATRASADO", "vermelho"
        else:
            self.status_label, self.cor = "A CAMINHO", "amarelo"


class PainelPedidosVM:
    def __init__(self, pedidos, hoje):
        self.itens = [PedidoViewModel(p, hoje) for p in pedidos]
        self.atrasados = sum(1 for i in self.itens if i.atrasado)
        self.rodape = f"{self.atrasados} pedido(s) atrasado(s)" if self.atrasados else "Tudo em dia"


# ---------------------------------------------------------------------------
# VIEW burra: só costura. Zero if, zero conta.
# ---------------------------------------------------------------------------
def tela_pedidos_mvvm(pedidos, hoje):
    painel = PainelPedidosVM(pedidos, hoje)
    linhas = [f"#{i.id} {i.cliente} - {i.total_formatado} - {i.status_label} ({i.cor})"
              for i in painel.itens]
    return "\n".join(linhas) + "\n" + painel.rodape


# Para explicar na P3:
# - "Cupom só acima de R$ 100" e "atrasado" são regras do NEGÓCIO → Service (testáveis sem tela,
#   reaproveitáveis pela API mobile). "vermelho" e "R$ 90.00" são EXIBIÇÃO → ViewModel.
# - Se a cor mudar, mexo só no VM; se a regra do cupom mudar, mexo só no Service.
