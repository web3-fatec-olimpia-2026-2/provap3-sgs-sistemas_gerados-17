# LAB Aula 04 — Polimorfismo: muitos quartos, uma função (RESOLVIDO)
#
# Ideia da aula: UMA função (imprimir_diaria) trata MUITOS tipos sem perguntar
# qual é qual. Cada tipo responde a seu modo → polimorfismo.


class Quarto:
    """Classe base: o comportamento PADRÃO de todo quarto."""

    def __init__(self, numero):
        self.numero = numero

    def descricao(self):
        return "Quarto comum"

    def preco_noite(self):
        return 200


class Suite(Quarto):
    """Suite É-UM Quarto (herança).

    - HERDA o __init__ (não precisei reescrever o construtor: ganha `numero` de graça).
    - SOBRESCREVE (override) descricao() e preco_noite(): mesmo nome, outra resposta.
    Herança traz o que é igual; sobrescrever muda o que é diferente.
    """

    def descricao(self):
        return "Suite"

    def preco_noite(self):
        return 500


class Presidencial(Quarto):
    def descricao(self):
        return "Quarto presidencial"

    def preco_noite(self):
        return 1200


# ⭐ Desafio: uma categoria nova. Repare que NADA abaixo precisou mudar para aceitá-la.
class Chale(Quarto):
    def descricao(self):
        return "Chale"

    def preco_noite(self):
        return 350


class QuartoStandard(Quarto):
    """Exemplo da FAQ (Q6): subtipo que NÃO sobrescreve nada.

    Quando alguém chama preco_noite(), o Python procura na classe filha, não acha,
    e sobe para a classe mãe → usa o comportamento padrão (200).
    """


# --- função polimórfica: JÁ VINHA PRONTA e NÃO foi alterada ---
def imprimir_diaria(quarto):
    # Não há "if quarto.tipo == ..." aqui. A função só CONFIA que todo quarto
    # sabe responder descricao() e preco_noite(). O Python decide, em tempo de
    # execução, qual versão do método chamar, pelo tipo REAL do objeto recebido.
    return f"{quarto.descricao()}: R$ {quarto.preco_noite()}"


# --- O que a aula pediu para NÃO fazer (guardado só para comparação) ---
def imprimir_diaria_com_if(quarto):
    """Versão SEM polimorfismo: um if que cresce a cada tipo novo.

    Para aceitar o Chalé seria preciso EDITAR esta função (e arriscar quebrar as outras).
    """
    if isinstance(quarto, Presidencial):
        return "Quarto presidencial: R$ 1200"
    elif isinstance(quarto, Suite):
        return "Suite: R$ 500"
    else:
        return "Quarto comum: R$ 200"   # o Chalé cairia aqui, ERRADO, sem aviso


if __name__ == "__main__":
    # Passo 4 do roteiro: uma lista com vários tipos, um for, uma função.
    quartos = [Quarto(101), Suite(201), Presidencial(301), Chale(401), QuartoStandard(501)]
    for q in quartos:
        print(imprimir_diaria(q))
