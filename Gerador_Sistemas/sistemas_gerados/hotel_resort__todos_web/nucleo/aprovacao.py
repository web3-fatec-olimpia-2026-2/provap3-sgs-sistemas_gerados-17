"""
Hotel Resort — CHAIN OF RESPONSIBILITY (GoF · comportamental): o pedido passa por uma CADEIA.

ANTES (nucleo/antes_aprovacao.py): quem_aprova_antigo(item) com if/elif de alçadas — incluir um
nível novo (ex.: supervisor) obriga a reescrever a função.
DEPOIS (aqui):
  * cada Aprovador conhece só a SUA alçada e o PRÓXIMO da cadeia;
  * aprovar(item): se pode, responde; se não, repassa ao próximo; no fim, ninguém aprovou;
  * a cadeia é montada de fora (encadear) → incluir/remover um nível não mexe nos outros.
Quando NÃO usar: regras fixas e poucas — um if/elif curto é mais simples de ler.
"""


class Aprovador:
    """ELO da cadeia: decide se aprova; se não, repassa ao próximo."""

    nome = "aprovador"
    limite = 0.0

    def __init__(self):
        self.proximo = None

    def encadear(self, proximo):
        """Liga o próximo elo e o DEVOLVE (permite a.encadear(b).encadear(c))."""
        self.proximo = proximo
        return proximo

    def aprovar(self, item):
        if item.total <= self.limite:
            return self.nome
        if self.proximo is None:
            return "sem aprovador"  # fim da cadeia: ninguém tinha alçada
        return self.proximo.aprovar(item)


class Atendente(Aprovador):
    nome, limite = "atendente", 500.0


class Gerente(Aprovador):
    nome, limite = "gerente", 2000.0


class Diretoria(Aprovador):
    nome, limite = "diretoria", 10000.0


class Supervisor(Aprovador):
    """Nível NOVO: entra na cadeia sem mudar nenhum outro aprovador."""

    nome, limite = "supervisor", 1000.0


def cadeia_padrao():
    """Monta atendente → gerente → diretoria e devolve o PRIMEIRO elo."""
    inicio = Atendente()
    inicio.encadear(Gerente()).encadear(Diretoria())
    return inicio
