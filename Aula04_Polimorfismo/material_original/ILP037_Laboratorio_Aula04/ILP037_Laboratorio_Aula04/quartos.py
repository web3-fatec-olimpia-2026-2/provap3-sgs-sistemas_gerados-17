# LAB Aula 04 - Polimorfismo: muitos quartos, uma funcao
#
# O Quarto base ja esta pronto. A funcao imprimir_diaria() tambem.
# Sua tarefa: criar Suite e Presidencial, que HERDAM de Quarto mas
# RESPONDEM de forma diferente aos metodos descricao() e preco_noite().
#
# Isso e POLIMORFISMO: o mesmo metodo, comportamentos diferentes.
# Siga o ROTEIRO.md.


class Quarto:
    def __init__(self, numero):
        self.numero = numero

    def descricao(self):
        return "Quarto comum"

    def preco_noite(self):
        return 200


# -----------------------------------------------------------------------
# SUA TAREFA 1: criar a classe Suite, que E-UM Quarto, mas:
#   - descricao() devolve "Suite"
#   - preco_noite() devolve 500
#
# SUA TAREFA 2: criar a classe Presidencial, que E-UM Quarto, mas:
#   - descricao() devolve "Quarto presidencial"
#   - preco_noite() devolve 1200
#
# Dica: herde de Quarto e reescreva (sobrescreva) os dois metodos.
#   class Suite(Quarto):
#       def descricao(self):
#           return "Suite"
#       ...
# -----------------------------------------------------------------------


# --- funcao polimorfica: JA PRONTA, nao altere ---
# Ela trata qualquer Quarto igual, e cada um responde a seu modo.
def imprimir_diaria(quarto):
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"
