"""ANTES — o smell do Flyweight: um objeto de tipo de hóspede NOVO para cada registro."""


class TipoAntigo:
    def __init__(self, nome, fator):
        self.nome = nome
        self.fator = fator


TIPOS_ANTIGOS = {"comum": ("Comum", 1.0), "fidelidade": ("Fidelidade", 0.9), "parceiro": ("Parceiro", 0.8), "vip": ("VIP", 0.5)}


def registrar_antigo(item, chave):
    nome, fator = TIPOS_ANTIGOS[chave]
    return item, TipoAntigo(nome, fator)  # cópia repetida a cada registro


def valor_antigo(registro):
    item, tipo = registro
    return round(item.total * tipo.fator, 2)
