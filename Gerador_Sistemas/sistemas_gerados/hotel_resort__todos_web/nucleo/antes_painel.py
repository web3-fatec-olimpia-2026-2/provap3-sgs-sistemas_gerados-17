"""ANTES — a tela que decide como mostrar (status, rótulo, R$, rodapé) no meio do desenho."""


def tela_painel(itens):
    linhas = []
    livres = 0
    for item in itens:
        if item["disponivel"]:
            status = "livre"
            acao = "Reservar"
            livres += 1
        else:
            status = "INDISPONIVEL"
            acao = "(ocupado)"
        preco = f"R$ {item['preco']:.2f}"
        linhas.append(f"Quarto {item['codigo']} [{item['categoria']}] - {preco} - {status} - {acao}")
    if livres:
        rodape = f"{livres} quarto(s) livre(s)"
    else:
        rodape = "LOTADO - nenhum quarto livre"
    return "\n".join(linhas) + "\n" + rodape
