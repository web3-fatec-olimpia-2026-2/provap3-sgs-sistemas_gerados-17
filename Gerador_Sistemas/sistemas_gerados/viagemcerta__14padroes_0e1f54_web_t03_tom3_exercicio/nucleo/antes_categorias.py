"""ANTES — o smell do polimorfismo ausente: um if que cresce a cada categoria nova."""


def imprimir_preco(tipo):
    """Para a categoria "Aventura" seria preciso EDITAR esta função (e ela cai no else, errada)."""
    if tipo == "executivo":
        return "Pacote executivo: R$ 650.00 por noite"
    elif tipo == "luxo":
        return "Pacote luxo: R$ 1200.00 por noite"
    else:
        return "Pacote econômico: R$ 350.00 por noite"
