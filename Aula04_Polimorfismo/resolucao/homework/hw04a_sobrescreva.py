"""Homework 04a — Sobrescreva os métodos.

Pede: Presidencial + um terceiro tipo à escolha (escolhi Bangalô), ambos herdando de
Quarto e sobrescrevendo descricao() e preco_noite(); depois um laço que passa todos
pela MESMA função imprimir_diaria, sem nenhum if de tipo.
"""


class Quarto:
    def __init__(self, numero):
        self.numero = numero

    def descricao(self):
        return "Quarto comum"

    def preco_noite(self):
        return 200


class Presidencial(Quarto):
    # sobrescreve os DOIS métodos (mesma assinatura, resposta própria)
    def descricao(self):
        return "Quarto presidencial"

    def preco_noite(self):
        return 1200


class Bangalo(Quarto):
    """Meu tipo: bangalô à beira da piscina, com taxa de limpeza por noite."""

    TAXA_LIMPEZA = 40

    def descricao(self):
        return "Bangalo"

    def preco_noite(self):
        # O subtipo pode reaproveitar a regra da mãe com super() e acrescentar a sua.
        # Aqui: o dobro do quarto comum + taxa de limpeza = 2*200 + 40 = 440.
        return 2 * super().preco_noite() + self.TAXA_LIMPEZA


def imprimir_diaria(quarto):
    # Função polimórfica: não pergunta o tipo, só chama os métodos.
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"


if __name__ == "__main__":
    hospedagem = [Quarto(101), Presidencial(301), Bangalo(501)]
    for quarto in hospedagem:          # um laço, uma função, três comportamentos
        print(imprimir_diaria(quarto))
    # Saída:
    # Quarto comum: R$ 200
    # Quarto presidencial: R$ 1200
    # Bangalo: R$ 440
