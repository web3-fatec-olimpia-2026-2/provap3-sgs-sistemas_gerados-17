"""
Cooperativa Citrícola — POLIMORFISMO (Aula 04): muitas categorias, uma função.

ANTES (nucleo/antes_categorias.py): imprimir_preco(tipo) com if/elif por categoria.
DEPOIS: cada categoria SOBRESCREVE descricao() e preco_unidade(); imprimir_preco(categoria)
só chama os métodos — o Python escolhe a versão pelo tipo REAL do objeto.
Herdar = ganhar o que é igual · sobrescrever = mudar o que é diferente.
"""


class LaranjaPera:
    """Classe BASE: o comportamento PADRÃO de toda categoria."""

    def __init__(self, codigo):
        self.codigo = codigo

    def descricao(self):
        return 'Laranja Pera'

    def preco_unidade(self):
        return 38.0


class LaranjaValencia(LaranjaPera):
    """LaranjaValencia É-UM LaranjaPera: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Laranja Valência'

    def preco_unidade(self):
        return 40.0


class LimaoTahiti(LaranjaPera):
    """LimaoTahiti É-UM LaranjaPera: HERDA o __init__ e SOBRESCREVE descricao() e preco_unidade()."""

    def descricao(self):
        return 'Limão Tahiti'

    def preco_unidade(self):
        return 45.0


class TangerinaPonkan(LaranjaPera):
    """NOVA categoria: entrou SEM mudar imprimir_preco (aberto ao novo)."""

    def descricao(self):
        return 'Tangerina Ponkan'

    def preco_unidade(self):
        return 52.0


class LaranjaPeraPadrao(LaranjaPera):
    """Não sobrescreve nada: o Python procura o método aqui, não acha e SOBE para LaranjaPera."""


def imprimir_preco(categoria):
    """Função POLIMÓRFICA: não pergunta o tipo (zero if); cada categoria responde a seu modo."""
    return f"{categoria.descricao()}: R$ {categoria.preco_unidade():.2f} por caixa"
