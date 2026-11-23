"""
SERVICE (Aula 07): a regra de negócio da camada web — NÃO conhece request, HTML nem template.
Reaproveita o STRATEGY do núcleo (nucleo/politicas.py): o campo `tipo` do model escolhe a política.
"""
from nucleo.politicas import PoliticaAtacado, PoliticaComum, PoliticaFidelidade, PoliticaFuncionario

# Raiz de composição: um DICIONÁRIO escolhe a estratégia (não é if/elif — política nova = 1 linha aqui).
POLITICAS = {
    "comum": PoliticaComum(),
    "fidelidade": PoliticaFidelidade(),
    "atacado": PoliticaAtacado(),
    "funcionario": PoliticaFuncionario()
}


class PedidoService:
    def valor_final(self, obj):
        """Total do model (Decimal) → float → política do núcleo."""
        return POLITICAS[obj.tipo].aplicar(float(obj.total))

    def resumo(self, objetos):
        """Devolve DADOS: ([(obj, valor_final), ...], soma)."""
        itens = [(obj, self.valor_final(obj)) for obj in objetos]
        return itens, round(sum(valor for _, valor in itens), 2)
