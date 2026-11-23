# LAB Aula 07 — Extrair um Service testável sem HTTP (RESOLVIDO)
#
# ANTES: a "view" calculava o total com desconto (REGRA) e montava o texto
#        (APRESENTAÇÃO) no mesmo laço → para testar a conta era preciso chamar
#        a view inteira e procurar o número no meio do texto.
# DEPOIS:
#   RelatorioService  → só a regra; recebe dados, devolve DADOS; não sabe o que é web.
#   relatorio_reservas_view → fina: chama o service e só FORMATA (orquestra).
#
# É o SRP (Aula 06) em escala de CAMADAS. No Django (MVT):
#   models.py = dado · views.py = regra/orquestração (o "Controller" do MVC)
#   template  = apresentação · services.py = camada a mais onde a regra complexa mora.

RESERVAS = [
    {"hospede": "Ana", "diarias": 3, "valor": 200, "tipo": "fidelidade"},
    {"hospede": "Bruno", "diarias": 2, "valor": 150, "tipo": "comum"},
]


class RelatorioService:
    """SÓ a regra de negócio. Nada de request, HttpResponse, template ou texto."""

    # Tabela de descontos por tipo; tipo desconhecido → sem desconto (1.0),
    # exatamente como o "else: total = base" da view original.
    DESCONTOS = {"fidelidade": 0.90, "parceiro": 0.80}

    def __init__(self, reservas):
        self.reservas = reservas

    def _total_reserva(self, r):
        """Total de UMA reserva (o sublinhado indica: uso interno da classe)."""
        base = r["diarias"] * r["valor"]
        return base * self.DESCONTOS.get(r["tipo"], 1.0)

    def calcular(self):
        """Devolve DADOS: ([(hospede, total), ...], total_geral).

        Quem quiser texto, HTML, JSON ou PDF formata depois — a regra não liga.
        """
        linhas = [(r["hospede"], self._total_reserva(r)) for r in self.reservas]
        total_geral = sum(total for _, total in linhas)
        return linhas, total_geral


def relatorio_reservas_view(reservas, request=None):
    """A view ficou FINA: 1) pede os dados ao service  2) formata a resposta."""
    linhas, total_geral = RelatorioService(reservas).calcular()
    corpo = "\n".join(f"{nome}: R$ {total:.2f}" for nome, total in linhas)
    return f"RELATORIO\n{corpo}\nTOTAL: R$ {total_geral:.2f}"


# Ganho extra da separação: a MESMA regra serve outra "apresentação" (ex.: uma API JSON)
# sem duplicar a conta.
def relatorio_reservas_api(reservas, request=None):
    linhas, total_geral = RelatorioService(reservas).calcular()
    return {
        "itens": [{"hospede": nome, "total": round(total, 2)} for nome, total in linhas],
        "total_geral": round(total_geral, 2),
    }
