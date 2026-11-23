"""ANTES — o smell do Chain of Responsibility: if/elif com todas as alçadas num lugar só."""


def quem_aprova_antigo(item):
    if item.total <= 500.0:
        return "atendente"
    elif item.total <= 2000.0:
        return "gerente"
    elif item.total <= 10000.0:
        return "diretoria"
    else:
        return "sem aprovador"
