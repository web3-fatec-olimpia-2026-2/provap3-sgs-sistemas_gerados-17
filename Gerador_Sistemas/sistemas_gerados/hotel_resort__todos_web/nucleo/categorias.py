"""
Hotel Resort — POLIMORFISMO (Aula 04): muitas categorias, uma função.

ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
"""


class Quarto:
    """Classe BASE: o comportamento PADRÃO de toda categoria."""

    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Quarto comum'

    def preco_unidade(self):
        return 200.0


class Suite(Quarto):
    """Suite É-UM Quarto: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Suíte'

    def preco_unidade(self):
        return 500.0


class Presidencial(Quarto):
    """Presidencial É-UM Quarto: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Quarto presidencial'

    def preco_unidade(self):
        return 1200.0


class Chale(Quarto):
    """NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)."""

    def descricao(self):
        return 'Chalé'

    def preco_unidade(self):
        return 350.0


class QuartoPadrao(Quarto):
    """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para Quarto."""


def imprimir_preco(categoria):
    """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por noite"
