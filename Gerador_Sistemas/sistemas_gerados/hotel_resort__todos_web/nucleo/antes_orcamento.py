"""ANTES — o smell do Visitor: cada operação percorre as linhas perguntando o TIPO (if/elif)."""


def total_antigo(linhas):
    total = 0.0
    for linha in linhas:
        if linha[0] == "reserva":
            total += linha[1].total
        elif linha[0] == "extra":
            total += linha[2]
        elif linha[0] == "desconto":
            total -= linha[1]
    return round(total, 2)


def texto_antigo(linhas):
    partes = []
    for linha in linhas:
        if linha[0] == "reserva":
            partes.append(f"{linha[1].hospede}: R$ {linha[1].total:.2f}")
        elif linha[0] == "extra":
            partes.append(f"+ {linha[1]}: R$ {linha[2]:.2f}")
        elif linha[0] == "desconto":
            partes.append(f"- desconto: R$ {linha[1]:.2f}")
    return "\n".join(partes)
