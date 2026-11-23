"""
Aula 04 - SOLUCAO DE REFERENCIA (professor). NAO incluir no pacote do aluno.
Polimorfismo: Suite e Presidencial sobrescrevem; imprimir_diaria trata os tres.
5 testes verdes. Desafio Chale incluido.
"""

class Quarto:
    def __init__(self, numero):
        self.numero = numero
    def descricao(self):
        return "Quarto comum"
    def preco_noite(self):
        return 200

class Suite(Quarto):
    def descricao(self):
        return "Suite"
    def preco_noite(self):
        return 500

class Presidencial(Quarto):
    def descricao(self):
        return "Quarto presidencial"
    def preco_noite(self):
        return 1200

# desafio
class Chale(Quarto):
    def descricao(self):
        return "Chale"
    def preco_noite(self):
        return 350

def imprimir_diaria(quarto):
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"
