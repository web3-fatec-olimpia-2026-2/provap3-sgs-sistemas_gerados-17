"""ANTES — a tela que decide como mostrar (status, rótulo, R$, rodapé) no meio do desenho."""


def tela_painel(itens):
    linhas = []
    livres = 0
    for item in itens:
        if item["disponivel"]:
            status = "disponível"
            acao = "Solicitar"
            livres += 1
        else:
            status = "INDISPONÍVEL"
            acao = "(indisponível)"
        preco = f"R$ {item['preco']:.2f}"
        linhas.append(f"Recurso {item['codigo']} [{item['categoria']}] - {preco} - {status} - {acao}")
    if livres:
        rodape = f"{livres} recurso(s) disponível(is)"
    else:
        rodape = "SEM DISPONIBILIDADE"
    return "\n".join(linhas) + "\n" + rodape
