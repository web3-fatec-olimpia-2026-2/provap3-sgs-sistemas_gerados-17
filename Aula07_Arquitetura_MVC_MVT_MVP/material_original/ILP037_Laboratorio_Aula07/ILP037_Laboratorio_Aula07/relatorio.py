# LAB Aula 07 - Arquitetura: extrair um Service testavel sem HTTP
#
# A funcao abaixo imita uma VIEW do Django: recebe os dados e devolve o texto
# da resposta. O problema: ela MISTURA a regra de negocio (calcular o total com
# desconto) com a apresentacao (montar o texto). Para testar o calculo, voce e
# obrigado a chamar a view inteira e ler o texto - nao da para testar so a regra.
#
# Sua tarefa (siga o ROTEIRO.md): extrair um RelatorioService que faz SO o
# calculo e devolve DADOS (nao texto). A view fica fina: chama o service e formata.


RESERVAS = [
    {"hospede": "Ana", "diarias": 3, "valor": 200, "tipo": "fidelidade"},
    {"hospede": "Bruno", "diarias": 2, "valor": 150, "tipo": "comum"},
]


def relatorio_reservas_view(reservas, request=None):
    linhas = []
    total_geral = 0
    for r in reservas:
        base = r["diarias"] * r["valor"]
        if r["tipo"] == "fidelidade":
            total = base * 0.90
        elif r["tipo"] == "parceiro":
            total = base * 0.80
        else:
            total = base
        total_geral += total
        linhas.append(f"{r['hospede']}: R$ {total:.2f}")
    corpo = "\n".join(linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total_geral:.2f}"


# --------------------------------------------------------------------------
# SUA TAREFA:
#   1. Crie a classe RelatorioService, que recebe as reservas e tem um metodo
#      calcular() que devolve (linhas, total_geral) - onde linhas e uma lista
#      de tuplas (hospede, total). SO calculo, SEM texto.
#   2. Reescreva relatorio_reservas_view para usar o service e so FORMATAR.
#   A saida final tem que continuar identica.
# --------------------------------------------------------------------------
