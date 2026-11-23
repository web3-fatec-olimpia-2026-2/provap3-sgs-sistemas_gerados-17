"""
Aula 07 - SOLUCAO DE REFERENCIA (professor). NAO incluir no pacote do aluno.
Arquitetura: extrair RelatorioService (regra de negocio, testavel sem HTTP);
view fina que so orquestra e formata. 2 testes verdes; saida identica.
"""

RESERVAS = [
    {"hospede": "Ana", "diarias": 3, "valor": 200, "tipo": "fidelidade"},
    {"hospede": "Bruno", "diarias": 2, "valor": 150, "tipo": "comum"},
]

class RelatorioService:
    """SO a regra de negocio. Nao sabe o que e web. Testavel sozinho."""
    def __init__(self, reservas):
        self.reservas = reservas
    def _total_reserva(self, r):
        base = r["diarias"] * r["valor"]
        descontos = {"fidelidade": 0.90, "parceiro": 0.80}
        return base * descontos.get(r["tipo"], 1.0)
    def calcular(self):
        linhas = [(r["hospede"], self._total_reserva(r)) for r in self.reservas]
        return linhas, sum(t for _, t in linhas)

def relatorio_reservas_view(reservas, request=None):
    linhas, total_geral = RelatorioService(reservas).calcular()
    corpo = "\n".join(f"{nome}: R$ {total:.2f}" for nome, total in linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total_geral:.2f}"

# MVC/MVT/MVP: todas separam dado / regra / apresentacao. O Service e a camada
# onde a regra complexa mora, entre a View e o Model, testavel sem HTTP.
# No Django (MVT): Model=dados, View=logica (o "Controller" do MVC), Template=apresentacao.
