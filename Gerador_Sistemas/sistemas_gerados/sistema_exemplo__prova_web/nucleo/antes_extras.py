"""ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


def preco_com_flags(item, urgente=False, embalagem=False, seguro=False):
    total = item.total
    if urgente:
        total += 30.0
    if embalagem:
        total += 10.0
    if seguro:
        total += 15.0
    return round(total, 2)
