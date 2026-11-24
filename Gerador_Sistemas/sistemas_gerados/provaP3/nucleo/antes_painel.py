"""ANTES — a tela que decide como mostrar (status, rótulo, R$, rodapé) no meio do desenho."""


def tela_painel(itens):
    linhas = []
    livres = 0
    for item in itens:
        if item["disponivel"]:
            status = "pronto para colher"
            acao = "Colher"
            livres += 1
        else:
            status = "EM COLHEITA"
            acao = "(em colheita)"
        preco = f"R$ {item['preco']:.2f}"
        linhas.append(f"Talhão {item['codigo']} [{item['categoria']}] - {preco} - {status} - {acao}")
    if livres:
        rodape = f"{livres} talhão(ões) pronto(s)"
    else:
        rodape = "ENTRESSAFRA - nenhum talhão pronto"
    return "\n".join(linhas) + "\n" + rodape
