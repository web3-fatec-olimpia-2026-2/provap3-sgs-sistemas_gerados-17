"""ANTES — o smell do Observer: quem altera chama cada interessado na mão (conhece todos)."""


def alterar_antigo(item, campo, valor, painel, log):
    setattr(item, campo, valor)
    painel["total"] = item.total
    log.append(f"{campo} -> {valor} (total R$ {item.total:.2f})")
