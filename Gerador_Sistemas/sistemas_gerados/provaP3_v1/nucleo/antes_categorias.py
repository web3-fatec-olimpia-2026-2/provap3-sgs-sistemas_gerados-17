"""ANTES — o smell do polimorfismo ausente: um if que cresce a cada categoria nova."""


def imprimir_preco(tipo):
    """Para a categoria "TangerinaPonkan" seria preciso EDITAR esta função (e ela cai no else, errada)."""
    if tipo == "laranja_valencia":
        return "Laranja Valência: R$ 40.00 por caixa"
    elif tipo == "limao_tahiti":
        return "Limão Tahiti: R$ 45.00 por caixa"
    else:
        return "Laranja Pera: R$ 38.00 por caixa"
