"""ANTES — o smell do Prototype: copiar campo por campo, na mão (e esquecer o que é novo)."""
from destinos.nucleo.entidades import Destino


def copiar_na_mao(original):
    return Destino(cliente=original.cliente, codigo=original.codigo, quantidade=original.quantidade, valor_unitario=original.valor_unitario, cidade=original.cidade, pais=original.pais, observacao=original.observacao)
