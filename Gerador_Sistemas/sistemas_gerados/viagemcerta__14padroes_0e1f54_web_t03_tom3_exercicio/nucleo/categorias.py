"""
ViagemCerta — POLIMORFISMO (Aula 04): muitas categorias, uma função.

ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
"""


class Economico:
    """Classe BASE: o comportamento PADRÃO de toda categoria."""

    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Pacote econômico'

    def preco_unidade(self):
        return 350.0


class Executivo(Economico):
    """Executivo É-UM Economico: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Pacote executivo'

    def preco_unidade(self):
        return 650.0


class Luxo(Economico):
    """Luxo É-UM Economico: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Pacote luxo'

    def preco_unidade(self):
        return 1200.0


class Aventura(Economico):
    """NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)."""

    def descricao(self):
        return 'Pacote aventura'

    def preco_unidade(self):
        return 480.0


class EconomicoPadrao(Economico):
    """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para Economico."""


def imprimir_preco(categoria):
    """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por noite"
