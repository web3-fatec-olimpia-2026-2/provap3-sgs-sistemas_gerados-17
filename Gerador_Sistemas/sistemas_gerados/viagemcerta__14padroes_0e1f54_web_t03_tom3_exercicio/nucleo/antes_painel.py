"""ANTES — a tela que decide como mostrar (status, rótulo, R$, rodapé) no meio do desenho."""


def tela_painel(itens):
    linhas = []
    livres = 0
    for item in itens:
        if item["disponivel"]:
            status = "com assentos"
            acao = "Reservar"
            livres += 1
        else:
            status = "ESGOTADO"
            acao = "(lista de espera)"
        preco = f"R$ {item['preco']:.2f}"
        linhas.append(f"Voo {item['codigo']} [{item['categoria']}] - {preco} - {status} - {acao}")
    if livres:
        rodape = f"{livres} voo(s) com assento"
    else:
        rodape = "ESGOTADO - nenhum voo com assento"
    return "\n".join(linhas) + "\n" + rodape
