"""ANTES — o smell do Builder: construtor com muitos argumentos POSICIONAIS (a ordem é decorada)."""
from nucleo.entidades import Reserva


def nova_reserva_antiga(hospede, quarto, diarias, valor_diaria, observacao=""):
    # Quem chama precisa lembrar a ORDEM: trocar dois números de lugar não dá erro, dá objeto errado.
    return Reserva(hospede, quarto, diarias, valor_diaria, observacao)
