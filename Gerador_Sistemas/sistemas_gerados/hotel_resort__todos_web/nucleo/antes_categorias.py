"""ANTES — o smell do polimorfismo ausente: um if que cresce a cada categoria nova."""


def imprimir_preco(tipo):
    """Para a categoria "Chale" seria preciso EDITAR esta função (e ela cai no else, errada)."""
    if tipo == "suite":
        return "Suíte: R$ 500.00 por noite"
    elif tipo == "presidencial":
        return "Quarto presidencial: R$ 1200.00 por noite"
    else:
        return "Quarto comum: R$ 200.00 por noite"
