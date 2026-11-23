from nucleo.entidades import Ingresso

DADOS_EXEMPLO = [
    {'espectador': 'Natália', 'sessao': 101, 'quantidade': 2, 'preco': 30.0},
    {'espectador': 'Otávio', 'sessao': 201, 'quantidade': 3, 'preco': 40.0},
    {'espectador': 'Paula', 'sessao': 301, 'quantidade': 1, 'preco': 25.5},
    {'espectador': 'Rafael', 'sessao': 401, 'quantidade': 4, 'preco': 0.0}
]


def dados(indice=0, **mudancas):
    copia = dict(DADOS_EXEMPLO[indice])
    copia.update(mudancas)
    return copia


def criar(indice=0, **mudancas):
    return Ingresso(**dados(indice, **mudancas))


def itens_exemplo():
    return [Ingresso(**d) for d in DADOS_EXEMPLO]
