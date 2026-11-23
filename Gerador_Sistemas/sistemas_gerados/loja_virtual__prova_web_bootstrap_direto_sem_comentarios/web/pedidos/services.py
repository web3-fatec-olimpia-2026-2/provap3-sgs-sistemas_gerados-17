from nucleo.politicas import PoliticaAtacado, PoliticaComum, PoliticaFidelidade, PoliticaFuncionario

POLITICAS = {
    "comum": PoliticaComum(),
    "fidelidade": PoliticaFidelidade(),
    "atacado": PoliticaAtacado(),
    "funcionario": PoliticaFuncionario()
}


class PedidoService:
    def valor_final(self, obj):
        return POLITICAS[obj.tipo].aplicar(float(obj.total))

    def resumo(self, objetos):
        itens = [(obj, self.valor_final(obj)) for obj in objetos]
        return itens, round(sum(valor for _, valor in itens), 2)
