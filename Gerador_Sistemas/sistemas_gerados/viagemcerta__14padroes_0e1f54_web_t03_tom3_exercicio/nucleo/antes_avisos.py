"""ANTES — o smell do Factory Method: if/elif para CRIAR o canal certo dentro do algoritmo."""


def avisar_antigo(item, canal):
    mensagem = f"Confirmação de Viagcert: R$ {item.total:.2f}"
    if canal == "email":
        return f"[e-mail] para {item.viajante}: {mensagem}"
    elif canal == "sms":
        return f"[sms] {item.viajante}: {mensagem[:60]}"
    else:
        raise ValueError(f"canal desconhecido: {canal}")
