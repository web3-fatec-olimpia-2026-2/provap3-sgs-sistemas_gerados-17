"""ANTES — o smell do Interpreter: a regra está ESCRITA NO CÓDIGO (mudar = programar de novo)."""


def regra_antiga(item):
    return item.quantidade >= 3 and item.total > 500 or item.valor_unitario == 0
