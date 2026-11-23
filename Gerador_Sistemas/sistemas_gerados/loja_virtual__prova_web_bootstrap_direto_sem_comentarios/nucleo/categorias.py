class Produto:
    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Produto comum'

    def preco_unidade(self):
        return 50.0


class Eletronico(Produto):
    def descricao(self):
        return 'Eletrônico'

    def preco_unidade(self):
        return 300.0


class Livro(Produto):
    def descricao(self):
        return 'Livro'

    def preco_unidade(self):
        return 40.0


class Alimento(Produto):
    def descricao(self):
        return 'Alimento'

    def preco_unidade(self):
        return 20.0


class ProdutoPadrao(Produto):
    pass


def imprimir_preco(categoria):
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por unidade"
