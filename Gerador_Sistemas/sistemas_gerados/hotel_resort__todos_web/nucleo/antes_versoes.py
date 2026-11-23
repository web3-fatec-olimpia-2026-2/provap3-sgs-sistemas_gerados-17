"""ANTES — o smell do Memento: copiar o interior (_campos) na mão para poder voltar atrás."""


def salvar_antigo(item):
    return {"_hospede": item._hospede, "_quarto": item._quarto, "_diarias": item._diarias, "_valor_diaria": item._valor_diaria, "observacao": item.observacao}


def restaurar_antigo(item, copia):
    for campo, valor in copia.items():
        setattr(item, campo, valor)
