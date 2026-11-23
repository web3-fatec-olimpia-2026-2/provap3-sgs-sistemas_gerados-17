"""ex03 — Service × ViewModel. SEU ARQUIVO (não mexa em tela_pedidos; resolva os TODOs)."""
from datetime import date

PEDIDOS = [
    {"id": 1, "cliente": "Ana",   "valor_itens": 100.0, "cupom": True,  "prazo": date(2026, 11, 20), "entregue": True},
    {"id": 2, "cliente": "Bruno", "valor_itens": 80.0,  "cupom": True,  "prazo": date(2026, 11, 18), "entregue": False},
    {"id": 3, "cliente": "Caio",  "valor_itens": 250.0, "cupom": False, "prazo": date(2026, 11, 30), "entregue": False},
]


def tela_pedidos(pedidos, hoje):
    """O SMELL: regra de negócio + exibição no mesmo laço."""
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


class PedidoService:
    def total(self, pedido):
        raise NotImplementedError   # TODO

    def esta_atrasado(self, pedido, hoje):
        raise NotImplementedError   # TODO


class PedidoViewModel:
    def __init__(self, pedido, hoje, servico=None):
        raise NotImplementedError   # TODO: id, cliente, total_formatado, status_label, cor


class PainelPedidosVM:
    def __init__(self, pedidos, hoje):
        raise NotImplementedError   # TODO: itens, atrasados, rodape


def tela_pedidos_mvvm(pedidos, hoje):
    raise NotImplementedError       # TODO: só costura o que o PainelPedidosVM preparou
