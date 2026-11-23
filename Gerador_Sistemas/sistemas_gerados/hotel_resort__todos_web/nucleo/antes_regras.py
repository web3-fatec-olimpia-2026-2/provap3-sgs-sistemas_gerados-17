"""ANTES — o smell do Interpreter: a regra está ESCRITA NO CÓDIGO (mudar = programar de novo)."""


def regra_antiga(item):
    return item.diarias >= 3 and item.total > 500 or item.valor_diaria == 0
