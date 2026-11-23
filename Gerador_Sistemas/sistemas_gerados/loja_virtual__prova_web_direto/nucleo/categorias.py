"""
Loja Virtual — POLIMORFISMO (Aula 04): muitas categorias, uma função.

ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
"""


class Produto:
    """Classe BASE: o comportamento PADRÃO de toda categoria."""

    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Produto comum'

    def preco_unidade(self):
        return 50.0


class Eletronico(Produto):
    """Eletronico É-UM Produto: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Eletrônico'

    def preco_unidade(self):
        return 300.0


class Livro(Produto):
    """Livro É-UM Produto: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Livro'

    def preco_unidade(self):
        return 40.0


class Alimento(Produto):
    """NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)."""

    def descricao(self):
        return 'Alimento'

    def preco_unidade(self):
        return 20.0


class ProdutoPadrao(Produto):
    """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para Produto."""


def imprimir_preco(categoria):
    """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por unidade"
