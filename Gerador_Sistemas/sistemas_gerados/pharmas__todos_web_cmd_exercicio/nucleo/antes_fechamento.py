"""ANTES — o smell do Template Method: o mesmo roteiro COPIADO em cada variação."""


def fechar_padrao_antigo(item):
    if item.total < 0:
        raise ValueError("total negativo")
    valor = item.total
    return f"R$ {valor:.2f}"


def fechar_com_taxa_antigo(item):
    if item.total < 0:
        raise ValueError("total negativo")
    valor = item.total
    valor = round(valor * 1.1, 2)
    return f"R$ {valor:.2f}"
