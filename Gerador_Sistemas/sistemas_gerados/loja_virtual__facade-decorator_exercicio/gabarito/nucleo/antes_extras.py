"""ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


def preco_com_flags(item, embrulho=False, cartao=False, entrega_expressa=False):
    total = item.total
    if embrulho:
        total += 15.0
    if cartao:
        total += 5.0
    if entrega_expressa:
        total += 25.0
    return round(total, 2)
