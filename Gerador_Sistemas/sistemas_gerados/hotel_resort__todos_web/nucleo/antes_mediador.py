"""ANTES — o smell do Mediator: cada componente conhece e altera os outros (todos acoplados)."""

FATORES = {"comum": 1.0, "fidelidade": 0.9, "parceiro": 0.8, "vip": 0.5}


class ResumoAntigo:
    def __init__(self):
        self.texto = ""


class BotaoAntigo:
    def __init__(self):
        self.habilitado = False


class SeletorAntigo:
    def __init__(self):
        self.valor = "comum"


class CampoAntigo:
    def __init__(self, preco, seletor, resumo, botao):
        # o campo precisa conhecer TODOS os outros para atualizar a tela
        self.preco, self.seletor, self.resumo, self.botao = preco, seletor, resumo, botao
        self.valor = 1

    def digitar(self, valor):
        self.valor = valor
        if isinstance(valor, int) and valor >= 1:
            total = round(valor * self.preco * FATORES[self.seletor.valor], 2)
            self.resumo.texto = f"{valor} diária(s) · R$ {total:.2f}"
            self.botao.habilitado = True
        else:
            self.resumo.texto = "diarias inválido(a)"
            self.botao.habilitado = False
