"""
Sistema Exemplo — Camada de SERVICE (Aula 07): a regra de negócio não sabe o que é web.

MVC (Model·Controller·View) · MVT do Django (Model·View·Template) · MVP (Model·Presenter·View):
todas separam DADO, REGRA e APRESENTAÇÃO. Aqui:
  RelatorioService → só a regra; recebe e devolve DADOS (testável sem HTTP)
  relatorio_view   → fina: chama o service e formata texto
  relatorio_api    → outra apresentação reaproveitando a MESMA regra
Quando NÃO usar: view que só lista e renderiza não precisa de Service.
"""

REGISTROS = [
    {'nome': 'Ana', 'quantidade': 2, 'preco': 100.0, 'tipo': 'comum'},
    {'nome': 'Bruno', 'quantidade': 3, 'preco': 49.9, 'tipo': 'especial'},
    {'nome': 'Carla', 'quantidade': 1, 'preco': 250.0, 'tipo': 'parceiro'},
    {'nome': 'Diego', 'quantidade': 4, 'preco': 0.0, 'tipo': 'comum'}
]


class RelatorioService:
    """SÓ a regra de negócio (desconto por tipo de cliente). Nada de request, HTML ou template."""

    FATORES = {"especial": 0.9, "parceiro": 0.8}  # tipo sem desconto → fator 1.0

    def __init__(self, registros):
        self.registros = registros

    def _total(self, registro):
        base = registro["quantidade"] * registro["preco"]
        return base * self.FATORES.get(registro["tipo"], 1.0)

    def calcular(self):
        """Devolve DADOS: ([(nome, total), ...], total_geral)."""
        linhas = [(r["nome"], self._total(r)) for r in self.registros]
        total_geral = sum(total for _, total in linhas)
        return linhas, total_geral


def relatorio_view(registros, request=None):
    """View FINA: 1) pede os dados ao service  2) formata a resposta."""
    linhas, total_geral = RelatorioService(registros).calcular()
    corpo = "\n".join(f"{nome}: R$ {total:.2f}" for nome, total in linhas)
    return f"RELATORIO - Sistema Exemplo\n{corpo}\nTOTAL: R$ {total_geral:.2f}"


def relatorio_api(registros, request=None):
    """Outra apresentação (JSON) com a mesma regra — sem duplicar a conta."""
    linhas, total_geral = RelatorioService(registros).calcular()
    return {"itens": [{"nome": nome, "total": round(total, 2)} for nome, total in linhas],
            "total_geral": round(total_geral, 2)}
