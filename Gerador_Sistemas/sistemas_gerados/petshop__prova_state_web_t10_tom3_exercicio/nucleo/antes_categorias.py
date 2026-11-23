"""ANTES — o smell do polimorfismo ausente: um if que cresce a cada categoria nova."""


def imprimir_preco(tipo):
    """Para a categoria "Personalizado" seria preciso EDITAR esta função (e ela cai no else, errada)."""
    if tipo == "intermediario":
        return "Intermediário: R$ 200.00 por unidade"
    elif tipo == "premium":
        return "Premium: R$ 400.00 por unidade"
    else:
        return "Básico: R$ 100.00 por unidade"
