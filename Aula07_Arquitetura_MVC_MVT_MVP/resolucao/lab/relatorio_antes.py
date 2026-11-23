# ANTES (código original do lab) — a view "faz-tudo". Guardado para provar saída idêntica.


def relatorio_reservas_view(reservas, request=None):
    linhas = []
    total_geral = 0
    for r in reservas:
        base = r["diarias"] * r["valor"]
        if r["tipo"] == "fidelidade":          # ← regra de negócio presa na view
            total = base * 0.90
        elif r["tipo"] == "parceiro":
            total = base * 0.80
        else:
            total = base
        total_geral += total
        linhas.append(f"{r['hospede']}: R$ {total:.2f}")   # ← apresentação
    corpo = "\n".join(linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total_geral:.2f}"
