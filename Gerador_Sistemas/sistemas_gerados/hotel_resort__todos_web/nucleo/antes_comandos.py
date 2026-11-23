"""ANTES — o smell do Command: a ação acontece direto e some (não dá para desfazer)."""


def alterar_antigo(item, campo, valor):
    setattr(item, campo, valor)
