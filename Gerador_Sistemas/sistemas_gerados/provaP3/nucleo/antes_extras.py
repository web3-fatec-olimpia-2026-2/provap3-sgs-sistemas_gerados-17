"""ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


def preco_com_flags(item, frete=False, classificacao=False, camara_fria=False):
    total = item.total
    if frete:
        total += 120.0
    if classificacao:
        total += 60.0
    if camara_fria:
        total += 90.0
    return round(total, 2)
