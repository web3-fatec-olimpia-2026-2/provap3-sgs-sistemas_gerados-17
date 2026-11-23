"""ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


def preco_com_flags(item, cafe_da_manha=False, transfer=False, late_checkout=False):
    total = item.total
    if cafe_da_manha:
        total += 40.0
    if transfer:
        total += 80.0
    if late_checkout:
        total += 60.0
    return round(total, 2)
