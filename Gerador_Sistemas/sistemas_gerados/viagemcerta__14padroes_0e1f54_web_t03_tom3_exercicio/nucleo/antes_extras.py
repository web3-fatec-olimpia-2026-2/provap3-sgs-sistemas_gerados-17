"""ANTES — o smell do Decorator: uma pilha de flags e ifs (cada extra novo = parâmetro + if)."""


def preco_com_flags(item, seguro_viagem=False, translado=False, passeio_guiado=False):
    total = item.total
    if seguro_viagem:
        total += 90.0
    if translado:
        total += 120.0
    if passeio_guiado:
        total += 150.0
    return round(total, 2)
