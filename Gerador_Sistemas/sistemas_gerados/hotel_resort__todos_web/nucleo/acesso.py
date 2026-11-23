"""
Hotel Resort — PROXY (GoF · estrutural): um SUBSTITUTO com a mesma interface que controla o acesso.

ANTES (nucleo/antes_acesso.py): quem consulta faz o cache e confere a permissão na mão, misturado
com a chamada — cada ponto de uso repete (ou esquece) essas regras.
DEPOIS (aqui):
  * ConsultaDePreco é o objeto REAL (imagine que é lento: banco, rede);
  * ConsultaComCache (proxy de CACHE) guarda respostas e só chama o real na primeira vez;
  * ConsultaProtegida (proxy de PROTEÇÃO) só deixa passar perfis autorizados;
  * todos têm o MESMO método calcular(item) → quem usa não percebe (e os proxies empilham).
Proxy × Decorator: os dois embrulham com a mesma interface; o Decorator ACRESCENTA comportamento,
o Proxy CONTROLA o acesso ao objeto real (cache, permissão, criação tardia, chamada remota).
"""

PERFIS_AUTORIZADOS = ("gerente", "atendente")


class ConsultaDePreco:
    """SUJEITO REAL: o cálculo "caro" (conta quantas vezes foi chamado)."""

    def __init__(self):
        self.chamadas = 0

    def calcular(self, item):
        self.chamadas += 1
        return item.total


class ConsultaComCache:
    """PROXY DE CACHE: mesma interface; só chama o real quando ainda não sabe a resposta."""

    def __init__(self, real):
        self._real = real
        self._cache = {}

    def calcular(self, item):
        chave = (item.hospede, item.diarias, item.valor_diaria)  # tudo que muda o resultado
        if chave not in self._cache:
            self._cache[chave] = self._real.calcular(item)
        return self._cache[chave]


class ConsultaProtegida:
    """PROXY DE PROTEÇÃO: mesma interface; barra quem não tem permissão."""

    def __init__(self, real, perfil):
        self._real = real
        self.perfil = perfil

    def calcular(self, item):
        if self.perfil not in PERFIS_AUTORIZADOS:
            raise PermissionError(f"perfil sem acesso: {self.perfil}")
        return self._real.calcular(item)
