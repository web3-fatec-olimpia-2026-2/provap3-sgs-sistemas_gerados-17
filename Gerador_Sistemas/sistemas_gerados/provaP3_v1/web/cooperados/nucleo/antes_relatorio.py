"""ANTES — a "view" que faz tudo: regra de negócio + apresentação no mesmo laço."""


def relatorio_view(registros, request=None):
    linhas = []
    total_geral = 0
    for r in registros:
        base = r["quantidade"] * r["preco"]
        # ↓ regra de negócio presa na view
        if r["tipo"] == "especial":
            total = base * 0.9
        elif r["tipo"] == "parceiro":
            total = base * 0.8
        else:
            total = base
        total_geral += total
        linhas.append(f"{r['nome']}: R$ {total:.2f}")  # ← apresentação
    corpo = "\n".join(linhas)
    return f"RELATORIO - Cooperativa Citrícola\n{corpo}\nTOTAL: R$ {total_geral:.2f}"
