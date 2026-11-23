"""ANTES — o smell do Composite: isinstance para saber se é lista ou item (em cada operação)."""


def total_antigo(coisa):
    if isinstance(coisa, list):
        return round(sum(total_antigo(parte) for parte in coisa), 2)
    return coisa.total
