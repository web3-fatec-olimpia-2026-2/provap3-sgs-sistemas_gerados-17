"""ANTES — o smell do Prototype: copiar campo por campo, na mão (e esquecer o que é novo)."""
from nucleo.entidades import Pharm


def copiar_na_mao(original):
    return Pharm(cliente=original.cliente, codigo=original.codigo, quantidade=original.quantidade, valor_unitario=original.valor_unitario, produto=original.produto, idade=original.idade, categoria=original.categoria, cosmeticos=original.cosmeticos, medicamentos=original.medicamentos, observacao=original.observacao)
