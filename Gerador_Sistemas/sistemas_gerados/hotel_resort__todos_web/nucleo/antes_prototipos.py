"""ANTES — o smell do Prototype: copiar campo por campo, na mão (e esquecer o que é novo)."""
from nucleo.entidades import Reserva


def copiar_na_mao(original):
    return Reserva(hospede=original.hospede, quarto=original.quarto, diarias=original.diarias, valor_diaria=original.valor_diaria, observacao=original.observacao)
