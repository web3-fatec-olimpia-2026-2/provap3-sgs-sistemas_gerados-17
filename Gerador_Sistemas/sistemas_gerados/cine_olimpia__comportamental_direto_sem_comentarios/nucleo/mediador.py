FATORES = {"inteira": 1.0, "meia": 0.5, "clube": 0.8, "promocional": 0.6}


class Componente:
    def __init__(self, mediador):
        self.mediador = mediador


class CampoQuantidade(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.valor = 1

    def digitar(self, valor):
        self.valor = valor
        self.mediador.notificar(self, "mudou")


class SeletorTipo(Componente):
    def __init__(self, mediador):
        super().__init__(mediador)
        self.valor = "inteira"

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
    def __init__(self, preco):
        self.preco = preco
        self.quantidade = CampoQuantidade(self)
        self.tipo = SeletorTipo(self)
        self.resumo = Resumo(self)
        self.botao = BotaoConfirmar(self)
        self.notificar(self.quantidade, "inicio")

    def notificar(self, origem, evento):
        valido = isinstance(self.quantidade.valor, int) and self.quantidade.valor >= 1
        if valido:
            valor = round(self.quantidade.valor * self.preco * FATORES[self.tipo.valor], 2)
            self.resumo.texto = f"{self.quantidade.valor} ingresso(s) · R$ {valor:.2f}"
        else:
            self.resumo.texto = "quantidade inválido(a)"
        self.botao.habilitado = valido
