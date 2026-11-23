"""ANTES — o smell do Abstract Factory: um if por PEÇA; esquecer um mistura as famílias."""


def montar_relatorio_antigo(itens, formato):
    if formato == "texto":
        partes = ["== Hotel Resort =="]
    else:
        partes = ["<h1>Hotel Resort</h1>"]
    for item in itens:
        if formato == "texto":
            partes.append(f"{item.hospede}: R$ {item.total:.2f}")
        else:
            partes.append(f"<li>{item.hospede}: R$ {item.total:.2f}</li>")
    total = round(sum(item.total for item in itens), 2)
    if formato == "texto":
        partes.append(f"TOTAL: R$ {total:.2f}")
    else:
        partes.append(f"<p><strong>TOTAL: R$ {total:.2f}</strong></p>")
    return "\n".join(partes)
