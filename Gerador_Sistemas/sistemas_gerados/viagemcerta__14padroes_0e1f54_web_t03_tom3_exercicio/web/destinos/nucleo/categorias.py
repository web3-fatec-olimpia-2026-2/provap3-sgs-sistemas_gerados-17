"""
ViagemCerta — POLIMORFISMO (Aula 04): muitas categorias, uma função.

ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
"""


class Basico:
    """Classe BASE: o comportamento PADRÃO de toda categoria."""

    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Básico'

    def preco_unidade(self):
        return 100.0


class Intermediario(Basico):
    """Intermediario É-UM Basico: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Intermediário'

    def preco_unidade(self):
        return 200.0


class Premium(Basico):
    """Premium É-UM Basico: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Premium'

    def preco_unidade(self):
        return 400.0


class Personalizado(Basico):
    """NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)."""

    def descricao(self):
        return 'Personalizado'

    def preco_unidade(self):
        return 300.0


class BasicoPadrao(Basico):
    """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para Basico."""


def imprimir_preco(categoria):
    """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por unidade"
