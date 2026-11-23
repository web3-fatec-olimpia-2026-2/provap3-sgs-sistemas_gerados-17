"""
Hotel Resort — MEDIATOR (GoF · comportamental): os componentes conversam por um CENTRO, não entre si.

ANTES (nucleo/antes_mediador.py): o campo de diarias conhecia o resumo e o botão e mexia neles direto —
cada componente novo obrigava a mexer nos outros (todos acoplados a todos).
DEPOIS (aqui):
  * cada componente só conhece o MEDIADOR e avisa: mediador.notificar(self, evento);
  * FormularioMediador decide quem reage: recalcula o resumo e liga/desliga o botão;
  * componente novo conversa só com o mediador (N ligações em vez de N × N).
Quando NÃO usar: 2–3 objetos que conversam pouco. Cuidado para o mediador não virar "objeto deus".
"""

FATORES = {"comum": 1.0, "fidelidade": 0.9, "parceiro": 0.8, "vip": 0.5}  # tipo de hóspede → fator


class Componente:
    """Todo componente conhece SÓ o mediador."""

    def __init__(self, mediador):
        self.mediador = mediador


class CampoDiarias(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.valor = 1

    def digitar(self, valor):
        self.valor = valor
        self.mediador.notificar(self, "mudou")  # não sabe QUEM vai reagir


class SeletorTipo(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.valor = "comum"

    def escolher(self, chave):
        self.valor = chave
        self.mediador.notificar(self, "mudou")


class Resumo(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.texto = ""


class BotaoConfirmar(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.habilitado = False


class FormularioMediador:
    """MEDIADOR: conhece todos os componentes e coordena as reações."""

    def __init__(self, preco):
        self.preco = preco
        self.quantidade = CampoDiarias(self)
        self.tipo = SeletorTipo(self)
        self.resumo = Resumo(self)
        self.botao = BotaoConfirmar(self)
        self.notificar(self.quantidade, "inicio")

    def notificar(self, origem, evento):
        valido = isinstance(self.quantidade.valor, int) and self.quantidade.valor >= 1
        if valido:
            valor = round(self.quantidade.valor * self.preco * FATORES[self.tipo.valor], 2)
            self.resumo.texto = f"{self.quantidade.valor} diária(s) · R$ {valor:.2f}"
        else:
            self.resumo.texto = "diarias inválido(a)"
        self.botao.habilitado = valido
