"""ANTES — o smell do Builder: construtor com muitos argumentos POSICIONAIS (a ordem é decorada)."""
from destinos.nucleo.entidades import Destino


def nova_destino_antiga(cliente, codigo, quantidade, valor_unitario, cidade, pais, observacao=""):
    # Quem chama precisa lembrar a ORDEM: trocar dois números de lugar não dá erro, dá objeto errado.
    return Destino(cliente, codigo, quantidade, valor_unitario, cidade, pais, observacao)
