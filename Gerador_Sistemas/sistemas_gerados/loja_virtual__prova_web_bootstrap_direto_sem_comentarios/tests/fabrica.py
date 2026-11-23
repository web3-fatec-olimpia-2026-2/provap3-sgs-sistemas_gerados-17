from nucleo.entidades import Pedido

DADOS_EXEMPLO = [
    {'cliente': 'Juliana', 'produto': 101, 'quantidade': 2, 'preco_unitario': 50.0},
    {'cliente': 'Kleber', 'produto': 201, 'quantidade': 3, 'preco_unitario': 19.9},
    {'cliente': 'Larissa', 'produto': 301, 'quantidade': 1, 'preco_unitario': 300.0},
    {'cliente': 'Marcos', 'produto': 401, 'quantidade': 4, 'preco_unitario': 0.0}
]


def dados(indice=0, **mudancas):
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    return Pedido(**dados(indice, **mudancas))


def itens_exemplo():
    return [Pedido(**d) for d in DADOS_EXEMPLO]
