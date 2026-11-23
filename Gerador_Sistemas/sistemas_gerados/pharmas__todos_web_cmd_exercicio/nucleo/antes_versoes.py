"""ANTES — o smell do Memento: copiar o interior (_campos) na mão para poder voltar atrás."""


def salvar_antigo(item):
    return {"_cliente": item._cliente, "_codigo": item._codigo, "_quantidade": item._quantidade, "_valor_unitario": item._valor_unitario, "_produto": item._produto, "_idade": item._idade, "_categoria": item._categoria, "_cosmeticos": item._cosmeticos, "_medicamentos": item._medicamentos, "observacao": item.observacao}


def restaurar_antigo(item, copia):
    for campo, valor in copia.items():
        setattr(item, campo, valor)
