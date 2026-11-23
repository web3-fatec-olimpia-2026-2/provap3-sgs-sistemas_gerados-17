"""ANTES — o smell do Builder: construtor com muitos argumentos POSICIONAIS (a ordem é decorada)."""
from nucleo.entidades import Pharm


def nova_pharm_antiga(cliente, codigo, quantidade, valor_unitario, produto, idade, categoria, cosmeticos, medicamentos, observacao=""):
    # Quem chama precisa lembrar a ORDEM: trocar dois números de lugar não dá erro, dá objeto errado.
    return Pharm(cliente, codigo, quantidade, valor_unitario, produto, idade, categoria, cosmeticos, medicamentos, observacao)
